package com.sample.chequebackend;

import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.repository.CrudRepository;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

interface ChequeMgmtRepo extends CrudRepository<Cheque, String> {}

@SpringBootApplication
@RestController
@CrossOrigin(origins = "*")
public class ChequeMgmtBackendApplication {

    private static final Logger logger = LoggerFactory.getLogger(ChequeMgmtBackendApplication.class);

    @Autowired
    ChequeMgmtRepo chequeRepo;

    @Value("${HOSTNAME:not_set}")
    String host;

    @Value("${spring.profiles.active:none}")
    String appProfile;

    private String getInstanceId() {
        return !host.equals("not_set") ? host : "Localhost";
    }

    @GetMapping("/welcome")
    public String welcome() {
        return "Welcome!!\nApp running on " + this.getInstanceId() + " instance.";
    }

    @GetMapping("/cheques/list")
    public List<Cheque> listAllChequeDetails() {
        logger.info("Request: GET, Path: /cheques/list");
        List<Cheque> cheques = new ArrayList<>();
        chequeRepo.findAll().forEach(cheques::add);
        return cheques;
    }

    @PostMapping("/cheques/add")
    public String addChequeDetails(@RequestParam String chequeNo, @RequestParam Boolean approvalGranted) {
        Cheque newCheque = new Cheque(chequeNo, approvalGranted);
        chequeRepo.save(newCheque);
        logger.info("Request: POST, Path: /cheques/add, Cheque No: {}, Approved: {}", chequeNo, approvalGranted);
        return "Created new cheque details for ID: " + chequeNo;
    }

    @PostMapping("/cheques/remove")
    public String clearChequeFromQueue(@RequestParam String chequeNo) {
        if (chequeNo != null) {
            Cheque cheque = chequeRepo.findById(chequeNo).orElse(null);
            if (cheque != null) {
                chequeRepo.delete(cheque);
                logger.info("Request: DELETE, Path: /cheques/remove, Cheque No: {}", chequeNo);
                return "Cleared cheque with ID: " + chequeNo;
            }
        }
        return "No such cheque request received!";
    }

    public static void main(String[] args) {
        SpringApplication.run(ChequeMgmtBackendApplication.class, args);
    }
}

@Entity
class Cheque {
    @Id
    private String chequeNo;
    private Boolean approvalGranted;

    public Cheque() {}

    public Cheque(String chkNo, Boolean approved) {
        this.chequeNo = chkNo;
        this.approvalGranted = approved;
    }

    public String getChequeNo() {
        return chequeNo;
    }

    public Boolean getApprovalStatus() {
        return approvalGranted;
    }

    public void setChequeNo(String chkNo) {
        this.chequeNo = chkNo;
    }

    public void setApprovalStatus(Boolean approval) {
        this.approvalGranted = approval;
    }
}