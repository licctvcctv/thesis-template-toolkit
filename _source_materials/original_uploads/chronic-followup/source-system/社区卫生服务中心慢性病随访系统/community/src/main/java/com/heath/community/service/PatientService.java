package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.dto.PatientDTO;
import com.heath.community.entity.Patient;
import com.heath.community.mapper.PatientMapper;
import com.heath.community.mapper.RiskLevelConfigMapper;
import com.heath.community.service.DoctorService;
import com.heath.community.util.ExcelUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PatientService {
    private final PatientMapper patientMapper;
    private final DoctorService doctorService;
    private final RiskLevelConfigMapper riskLevelConfigMapper;

    public PageResult<PatientDTO> findPage(String name, String patientNo, String diseaseType,
                                           String riskLevel, Long doctorId, Long current, Long size) {
        Long offset = (current - 1) * size;
        var records = patientMapper.findPage(name, patientNo, diseaseType, riskLevel, doctorId, offset, size);
        Long total = patientMapper.count(name, patientNo, diseaseType, riskLevel, doctorId);
        return PageResult.of(records, total, current, size);
    }

    public PatientDTO findById(Long id) {
        return patientMapper.findById(id);
    }

    @Transactional
    public void add(Patient patient) {
        if (patient.getPatientNo() == null || patient.getPatientNo().isEmpty()) {
            patient.setPatientNo(generatePatientNo());
        } else {
            Patient existing = patientMapper.findByPatientNo(patient.getPatientNo());
            if (existing != null) {
                throw new RuntimeException("患者编号已存在");
            }
        }
        if (patient.getRiskLevel() == null) {
            patient.setRiskLevel("low");
        }
        if (patient.getStatus() == null) {
            patient.setStatus(1);
        }
        patientMapper.insert(patient);
    }

    @Transactional
    public void update(Patient patient) {
        PatientDTO existing = patientMapper.findById(patient.getId());
        if (existing == null) {
            throw new RuntimeException("患者不存在");
        }
        
        if (patient.getPatientNo() != null && !patient.getPatientNo().equals(existing.getPatientNo())) {
            Patient duplicate = patientMapper.findByPatientNo(patient.getPatientNo());
            if (duplicate != null && !duplicate.getId().equals(patient.getId())) {
                throw new RuntimeException("患者编号已存在");
            }
        }
        
        patientMapper.update(patient);
    }

    @Transactional
    public void delete(Long id) {
        PatientDTO patient = patientMapper.findById(id);
        if (patient == null) {
            throw new RuntimeException("患者不存在");
        }
        patientMapper.delete(id);
    }

    public void export(String name, String patientNo, String diseaseType, String riskLevel, HttpServletResponse response) throws IOException {
        PageResult<PatientDTO> pageResult = findPage(name, patientNo, diseaseType, riskLevel, null, 1L, 10000L);
        List<ExcelUtil.PatientExportData> exportDataList = new ArrayList<>();
        
        for (PatientDTO dto : pageResult.getRecords()) {
            ExcelUtil.PatientExportData exportData = new ExcelUtil.PatientExportData();
            exportData.setPatientNo(dto.getPatientNo());
            exportData.setName(dto.getName());
            exportData.setGender(dto.getGender());
            exportData.setBirthday(dto.getBirthday());
            exportData.setIdCard(dto.getIdCard());
            exportData.setPhone(dto.getPhone());
            exportData.setAddress(dto.getAddress());
            exportData.setDiseaseType(dto.getDiseaseType());
            exportData.setDiagnosisDate(dto.getDiagnosisDate());
            exportData.setRiskLevelName(dto.getRiskLevelName());
            exportData.setDoctorName(dto.getDoctorName());
            exportDataList.add(exportData);
        }
        
        ExcelUtil.exportPatient(exportDataList, response);
    }

    @Transactional
    public int importData(MultipartFile file) throws IOException {
        List<ExcelUtil.PatientImportData> importDataList = ExcelUtil.importPatient(file);
        int successCount = 0;
        int failCount = 0;
        
        for (ExcelUtil.PatientImportData importData : importDataList) {
            try {
                Patient patient = new Patient();
                patient.setPatientNo(importData.getPatientNo());
                patient.setName(importData.getName());
                patient.setGender(importData.getGender());
                patient.setBirthday(importData.getBirthday());
                patient.setIdCard(importData.getIdCard());
                patient.setPhone(importData.getPhone());
                patient.setAddress(importData.getAddress());
                patient.setDiseaseType(importData.getDiseaseType());
                patient.setDiagnosisDate(importData.getDiagnosisDate());
                
                if (importData.getRiskLevelName() != null && !importData.getRiskLevelName().isEmpty()) {
                    var riskLevels = riskLevelConfigMapper.findAllEnabled();
                    for (var rl : riskLevels) {
                        if (rl.getLevelName().equals(importData.getRiskLevelName())) {
                            patient.setRiskLevel(rl.getLevelCode());
                            break;
                        }
                    }
                }
                if (patient.getRiskLevel() == null) {
                    patient.setRiskLevel("low");
                }
                
                if (importData.getDoctorName() != null && !importData.getDoctorName().isEmpty()) {
                    var doctorPageResult = doctorService.findPage(null, null, null, 1L, 1000L);
                    for (var doctor : doctorPageResult.getRecords()) {
                        if (doctor.getName() != null && doctor.getName().equals(importData.getDoctorName())) {
                            patient.setCurrentDoctorId(doctor.getId());
                            break;
                        }
                    }
                }
                
                patient.setStatus(1);
                add(patient);
                successCount++;
            } catch (Exception e) {
                failCount++;
            }
        }
        
        if (failCount > 0) {
            throw new RuntimeException("导入完成，成功：" + successCount + "条，失败：" + failCount + "条");
        }
        
        return successCount;
    }

    private String generatePatientNo() {
        String dateStr = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String uuid = UUID.randomUUID().toString().replace("-", "").substring(0, 8).toUpperCase();
        return "P" + dateStr + uuid;
    }
}
