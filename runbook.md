# Sentinel Runbook
*Auto-generated from incident memory. Last updated by Reflect.*

# Runbook: Common Incident Patterns & Immediate Actions

- **Database Connection Pool Exhaustion**  
  *Symptoms:* latency spikes, `504` errors.  
  **Remediation:**  
  1. Check current `max-connections` in the service config.  
  2. Increase the pool limit by 25‑50 % (or to the service’s capacity).  
  3. Shorten `idle-timeout` and enable connection timeout.  
  4. Verify retry logic is enabled and add an alert for pool usage.  

- **Memory Leaks / OOM Crashes**  
  *Symptoms:* OOM kills, frequent restarts.  
  **Remediation:**  
  1. Review memory‑usage metrics; note the spike time.  
  2. Restart the affected pod/process to recover.  
  3. Collect a memory profile (`heapdump`, `jmap`, etc.).  
  4. Deploy a patch or enable automated restarts based on a memory‑threshold alert.  

- **Missing / Malformed Configuration**  
  *Symptoms:* startup failures, missing env vars.  
  **Remediation:**  
  1. Pull the latest config from the central repository.  
  2. Run the validation script (`config‑lint`) locally.  
  3. Apply the corrected config and redeploy the service.  
  4. Add the validation step to the CI pipeline.  

- **Expired TLS Certificates**  
  *Symptoms:* `SSLHandshakeException`, HTTPS failures.  
  **Remediation:**  
  1. Identify the expired cert via monitoring or `openssl s_client`.  
  2. Renew the certificate using the automated tool (e.g., Cert‑Manager, ACME).  
  3. Reload/restart the service to pick up the new cert.  
  4. Verify with `curl -v https://<service>` that the handshake succeeds.  

- **Deployment‑Related Regressions**  
  *Symptoms:* new errors appear after a release.  
  **Remediation:**  
  1. Roll back to the last known good version.  
  2. Run the full integration test suite against the rolled‑back version.  
  3. Open a ticket for the failing tests and add them to CI.  

- **Rate‑Limiting Issues**  
  *Symptoms:* `429 Too Many Requests`, throttled traffic.  
  **Remediation:**  
  1. Inspect the current rate‑limit configuration.  
  2. Adjust bucket size or thresholds as needed.  
  3. Enable exponential backoff in client code.  
  4. Monitor request‑queue depth and error rates.  

- **Deadlocks / Thread Leaks**  
  *Symptoms:* service hangs, thread dumps show waiting threads.  
  **Remediation:**  
  1. Capture a thread dump (`jstack`/`gstack`).  
  2. Identify any deadlocked threads.  
  3. Restart the service to break the deadlock.  
  4. File a bug for a code fix and add thread‑lifecycle tests.  
