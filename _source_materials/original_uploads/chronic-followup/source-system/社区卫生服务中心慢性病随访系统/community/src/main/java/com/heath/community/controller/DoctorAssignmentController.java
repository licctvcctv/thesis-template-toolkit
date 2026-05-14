package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.dto.DoctorAssignmentDTO;
import com.heath.community.service.DoctorAssignmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/doctor-assignment")
@RequiredArgsConstructor
public class DoctorAssignmentController {
    private final DoctorAssignmentService doctorAssignmentService;

    @GetMapping("/list")
    public Result<PageResult<DoctorAssignmentDTO>> list(@RequestParam(required = false) Long patientId,
                                                        @RequestParam(required = false) Long doctorId,
                                                        @RequestParam(defaultValue = "1") Long current,
                                                        @RequestParam(defaultValue = "10") Long size) {
        PageResult<DoctorAssignmentDTO> pageResult = doctorAssignmentService.findPage(patientId, doctorId, current, size);
        return Result.success(pageResult);
    }

    @GetMapping("/{id}")
    public Result<DoctorAssignmentDTO> getById(@PathVariable Long id) {
        DoctorAssignmentDTO assignment = doctorAssignmentService.findById(id);
        return Result.success(assignment);
    }

    @PostMapping("/assign")
    public Result<Void> assign(@RequestParam Long patientId,
                               @RequestParam Long doctorId,
                               @RequestParam Long assignerId,
                               @RequestParam(required = false) String remarks) {
        try {
            doctorAssignmentService.assign(patientId, doctorId, assignerId, remarks);
            return Result.success("分配成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
