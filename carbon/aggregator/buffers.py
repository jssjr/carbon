import time
from twisted.internet.task import LoopingCall
from carbon.conf import settings
from carbon import log, instrumentation

instrumentation.configure_stats('aggregation.compute_value_microseconds', ('total', 'min', 'max', 'avg'))

ONE_MILLION = 1000000 # I hate counting zeroes

class BufferManager:
  def __init__(self):
    self.buffers = {}

  def __len__(self):
    return len(self.buffers)

  def get_buffer(self, metric_path):
    if metric_path not in self.buffers:
      log.aggregator("Allocating new metric buffer for %s" % metric_path)
      self.buffers[metric_path] = MetricBuffer(metric_path)

    return self.buffers[metric_path]

  def clear(self):
    for buffer in self.buffers.values():
      buffer.close()

    self.buffers.clear()


class MetricBuffer:
  __slots__ = ('metric_path', 'interval_buffers', 'compute_task', 'configured',
               'aggregation_frequency', 'aggregation_func')

  def __init__(self, metric_path):
    self.metric_path = metric_path
    self.interval_buffers = {}
    self.compute_task = None
    self.configured = False
    self.aggregation_frequency = None
    self.aggregation_func = None

  def input(self, datapoint):
    (timestamp, value) = datapoint
    interval = timestamp - (timestamp % self.aggregation_frequency)
    if interval in self.interval_buffers:
      buffer = self.interval_buffers[interval]
    else:
      buffer = self.interval_buffers[interval] = IntervalBuffer(interval)

    buffer.input(datapoint)

  def configure_aggregation(self, frequency, func):
    self.aggregation_frequency = int(frequency)
    self.aggregation_func = func
    self.compute_task = LoopingCall(self.compute_value)
    self.compute_task.start(settings['AGGREGATION_WRITE_BACK_FREQUENCY'] or int(frequency), now=False)
    self.configured = True

  def compute_value(self):
    now = int( time.time() )
    current_interval = now - (now % self.aggregation_frequency)
    age_threshold = current_interval - (settings['MAX_AGGREGATION_INTERVALS'] * self.aggregation_frequency)

    for buffer in self.interval_buffers.values():
      # If the interval is the current one, then skip computing it for now.
      #  People get antsy about computed values being "wrong" when not enough data points are in
      if buffer.interval == current_interval:
        continue

      # If interval is too old, then delete it.
      if buffer.interval < age_threshold:
        del self.interval_buffers[buffer.interval]
        if not self.interval_buffers:
          self.close()
          self.configured = False
          del BufferManager.buffers[self.metric_path]
        continue

      # If buffer is active, then compute it.
      if buffer.active:
        value = self.aggregation_func(buffer.values)
        datapoint = (buffer.interval, value)
        state.events.metricGenerated(self.metric_path, datapoint)
        instrumentation.increment('aggregation.datapoints_generated')
        buffer.mark_inactive()
    duration_micros = (time.time() - now) * ONE_MILLION
    instrumentation.append('aggregation.compute_value_microseconds', duration_micros)

  def close(self):
    if self.compute_task and self.compute_task.running:
      self.compute_task.stop()

  @property
  def size(self):
    return sum([len(buf.values) for buf in self.interval_buffers.values()])


class IntervalBuffer:
  __slots__ = ('interval', 'values', 'active')

  def __init__(self, interval):
    self.interval = interval
    self.values = []
    self.active = True

  def input(self, datapoint):
    self.values.append( datapoint[1] )
    self.active = True

  def mark_inactive(self):
    self.active = False


# Shared importable singleton
BufferManager = BufferManager()

instrumentation.configure_metric_function(
  'aggregation.allocated_buffers',
  lambda: len(BufferManager)
)
instrumentation.configure_metric_function(
  'aggregation.buffered_datapoints',
  lambda: sum([b.size for b in BufferManager.buffers.values()])
)

# Avoid import circularity
from carbon import state
