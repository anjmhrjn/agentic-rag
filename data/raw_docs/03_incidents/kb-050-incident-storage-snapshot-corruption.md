---
doc_id: KB-050
doc_type:
  - incident
  - disaster-recovery
service: storage
date: 2024-03-15
---
### KB-050: Incident Response: Storage Snapshot Corruption
#### Symptoms and Alerts

- **Symptoms:** Attempting to restore a database (KB-021) or an EBS volume results in an Error or Corrupt state.

#### Impact Assessment

Critical. The backup strategy (Category 2) has failed.

#### Resolution Steps

1. **Identify Alternative Snapshot:** Locate the previous day's snapshot in the AWS Console.
2. **Cross-Region Check:** See if the secondary region (KB-014) has a healthy copy of the data.
3. **Contact AWS Support:** Open a P0 "Technical Support" case immediately.
4. **Manual Reconstruction:** As a last resort, use application-level logs (KB-013) to replay transactions into a fresh database.

#### Decisions &amp; Reasoning

- **Decision:** Mandatory "Backup Verification" drills held quarterly.
- **Reasoning:** A backup is only a backup if it actually restores. Verification drills reveal corruption *before* an incident occurs, ensuring that when a real disaster hits, we are 100% confident in our recovery path.