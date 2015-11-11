SELECT frame.frame_id, frame.frame_package, frame.frame_time from frame, job, machine
WHERE 
  machine.machine_id = 1 and 
  frame.frame_jobid = job.job_id and 
  frame.frame_status = 'WAITING' and 
  job.job_mincores <= machine.machine_cores and 
  job.job_minramgb <= machine.machine_ramgb and 
  job.job_mingpuramgb <= machine.machine_gpuramgb
ORDER BY job.job_priority DESC, 
  frame.frame_priority DESC, 
  frame.frame_package ASC,
  job.job_id ASC,
  frame.frame_time ASC;

