package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.dto.FollowupTaskDTO;
import com.heath.community.dto.FollowupTaskStatisticsDTO;
import com.heath.community.entity.FollowupTask;
import com.heath.community.mapper.FollowupTaskMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
public class FollowupTaskService {
    private final FollowupTaskMapper followupTaskMapper;

    public PageResult<FollowupTaskDTO> findPage(Long patientId, Long doctorId, String status,
                                               LocalDate startDate, LocalDate endDate, Integer page, Integer size) {
        Long offset = (long) (page - 1) * size;
        List<FollowupTaskDTO> list = followupTaskMapper.findPage(patientId, doctorId, status, startDate, endDate, offset, (long) size);
        Long total = followupTaskMapper.count(patientId, doctorId, status, startDate, endDate);
        return PageResult.of(list, total, (long) page, (long) size);
    }

    public FollowupTaskDTO findById(Long id) {
        return followupTaskMapper.findById(id);
    }

    @Transactional
    public void create(FollowupTask task) {
        if (task.getTaskNo() == null || task.getTaskNo().isEmpty()) {
            String taskNo = "FT" + System.currentTimeMillis();
            task.setTaskNo(taskNo);
        }
        if (task.getStatus() == null) {
            task.setStatus("pending");
        }
        if (task.getPriority() == null) {
            task.setPriority("normal");
        }
        if (task.getAssignDate() == null) {
            task.setAssignDate(LocalDate.now());
        }
        followupTaskMapper.insert(task);
    }

    @Transactional
    public void update(FollowupTask task) {
        followupTaskMapper.update(task);
    }

    @Transactional
    public void delete(Long id) {
        followupTaskMapper.delete(id);
    }

    @Transactional
    public void updateStatus(Long id, String status) {
        FollowupTask task = new FollowupTask();
        task.setId(id);
        task.setStatus(status);
        if ("completed".equals(status)) {
            task.setActualDate(LocalDate.now());
        }
        followupTaskMapper.update(task);
    }

    public FollowupTaskStatisticsDTO getStatistics() {
        FollowupTaskStatisticsDTO stats = new FollowupTaskStatisticsDTO();
        stats.setTotalTasks(followupTaskMapper.count(null, null, null, null, null));
        stats.setPendingTasks(followupTaskMapper.countByStatus("pending"));
        stats.setInProgressTasks(followupTaskMapper.countByStatus("in_progress"));
        stats.setCompletedTasks(followupTaskMapper.countByStatus("completed"));
        if (stats.getTotalTasks() > 0) {
            stats.setCompletionRate((double) stats.getCompletedTasks() / stats.getTotalTasks() * 100);
        } else {
            stats.setCompletionRate(0.0);
        }
        return stats;
    }
}
