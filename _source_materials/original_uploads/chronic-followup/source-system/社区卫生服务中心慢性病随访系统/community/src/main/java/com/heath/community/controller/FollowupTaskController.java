package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.dto.FollowupTaskDTO;
import com.heath.community.dto.FollowupTaskStatisticsDTO;
import com.heath.community.entity.FollowupTask;
import com.heath.community.service.FollowupTaskService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/followup-task")
@RequiredArgsConstructor
public class FollowupTaskController {
    private final FollowupTaskService followupTaskService;

    @GetMapping("/page")
    public Result<PageResult<FollowupTaskDTO>> findPage(
            @RequestParam(required = false) Long patientId,
            @RequestParam(required = false) Long doctorId,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        return Result.success(followupTaskService.findPage(patientId, doctorId, status, startDate, endDate, page, size));
    }

    @GetMapping("/{id}")
    public Result<FollowupTaskDTO> findById(@PathVariable Long id) {
        return Result.success(followupTaskService.findById(id));
    }

    @PostMapping
    public Result<Void> create(@RequestBody FollowupTask task, @RequestHeader(value = "Authorization", required = false) String token) {
        if (token != null && !token.isEmpty()) {
            try {
                Long userId = Long.parseLong(token);
                task.setCreatorId(userId);
            } catch (NumberFormatException e) {
            }
        }
        followupTaskService.create(task);
        return Result.success();
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody FollowupTask task) {
        task.setId(id);
        followupTaskService.update(task);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        followupTaskService.delete(id);
        return Result.success();
    }

    @PutMapping("/{id}/status")
    public Result<Void> updateStatus(@PathVariable Long id, @RequestParam String status) {
        followupTaskService.updateStatus(id, status);
        return Result.success();
    }

    @GetMapping("/statistics")
    public Result<FollowupTaskStatisticsDTO> getStatistics() {
        return Result.success(followupTaskService.getStatistics());
    }
}
