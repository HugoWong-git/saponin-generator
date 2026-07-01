#!/usr/bin/env python
"""
Autonomous coordinator for overnight RL experiments.
Monitors Plan B, then runs Plan C → Plan D → sampling → analysis.
"""
import subprocess, sys, os, time, json, re, signal

ROOT = "."
VENV_PYTHON = f"{ROOT}/venv/bin/python"
REINVENT = f"{VENV_PYTHON} -m reinvent"
ENV = os.environ.copy()
ENV["PYTHONPATH"] = f"{ROOT}/reinvent4_repo:{ENV.get('PYTHONPATH', '')}"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def run_reinvent(config, logfile, timeout=7200, max_retries=2):
    """Run a REINVENT command with retries."""
    cmd = f"cd {ROOT} && source venv/bin/activate && PYTHONPATH={ROOT}/reinvent4_repo:$PYTHONPATH {VENV_PYTHON} -m reinvent configs/{config} -l logs/{logfile}"
    for attempt in range(max_retries):
        log(f"Starting {config} (attempt {attempt+1})...")
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout,
            env={**ENV, "PATH": f"{ROOT}/venv/bin:{os.environ['PATH']}"}
        )
        exit_code = result.returncode
        # Check log for "Finished REINVENT"
        log_path = f"{ROOT}/logs/{logfile}"
        finished = False
        if os.path.exists(log_path):
            with open(log_path) as f:
                content = f.read()
                finished = "Finished REINVENT" in content
        if exit_code == 0 and finished:
            log(f"{config} completed successfully.")
            return True
        if attempt < max_retries - 1:
            log(f"Attempt {attempt+1} failed (code={exit_code}, finished={finished}), retrying...")
            time.sleep(10)
        else:
            log(f"FAILED: {config} after {max_retries} attempts")
    return False

def run_sampling(config, logfile, timeout=600):
    """Run a sampling job."""
    return run_reinvent(config, logfile, timeout=timeout)

def wait_for_steps(logpath, target_steps, check_interval=30):
    """Wait until a certain number of steps or Finished is reached."""
    while True:
        if not os.path.exists(logpath):
            time.sleep(check_interval)
            continue
        with open(logpath) as f:
            content = f.read()
        if "Finished REINVENT" in content:
            log("RL finished detected.")
            return True
        # Count steps
        steps = len(re.findall(r"Step:\s*\d+", content))
        if steps > 0:
            last_score = re.findall(r"Score:\s*([\d.]+)", content)
            last_nll = re.findall(r"NLL:\s*([\d.]+)", content)
            score_str = f"score={last_score[-1]}" if last_score else ""
            nll_str = f"NLL={last_nll[-1]}" if last_nll else ""
            log(f"  Step {steps}/{target_steps}  {score_str}  {nll_str}")
        if steps >= target_steps:
            return True
        time.sleep(check_interval)

# ── Step 1: Wait for Plan B to finish ──
log("=== Waiting for Plan B (Extreme IC50 RL) to finish ===")
wait_for_steps(f"{ROOT}/logs/rl_saponin_ic50_extreme.log", 500, check_interval=60)

# ── Step 2: Sample from Plan B agent (50k) ──
log("=== Plan B: Sampling 50k from extreme agent ===")
sampling_b_config = """run_type = "sampling"
[parameters]
model_file = \"""" + ROOT + """/models/saponin_ic50_extreme.chkpt"
num_smiles = 50000
output_file = \"""" + ROOT + """/samples/ic50_extreme_agent_samples.csv"
unique_molecules = true
randomize_smiles = true
temperature = 1.0
isomeric_smiles = false"""
with open(f"{ROOT}/configs/sampling/ic50_extreme_sampling.toml", "w") as f:
    f.write(sampling_b_config)

run_sampling("sampling/ic50_extreme_sampling.toml", "sampling/ic50_extreme_sampling.log", timeout=600)

# ── Step 3: Run Plan C (Light saponin RL) ──
log("=== Plan C: Running light saponin RL from E1 prior ===")
run_reinvent("rl_saponin_light_epoch1.toml", "rl_saponin_light_epoch1.log", timeout=7200)

# ── Step 4: Sample from Plan C agent (30k) ──
log("=== Plan C: Sampling 30k from light agent ===")
sampling_c_config = """run_type = "sampling"
[parameters]
model_file = \"""" + ROOT + """/models/saponin_light_e1_stage1.chkpt"
num_smiles = 30000
output_file = \"""" + ROOT + """/samples/saponin_light_epoch1_agent_samples.csv"
unique_molecules = true
randomize_smiles = true
temperature = 1.0
isomeric_smiles = false"""
with open(f"{ROOT}/configs/sampling/saponin_light_sampling.toml", "w") as f:
    f.write(sampling_c_config)
run_sampling("sampling/saponin_light_sampling.toml", "sampling/saponin_light_sampling.log", timeout=600)

# ── Step 5: Run Plan D (Generic prior RL) ──
log("=== Plan D: Running IC50 RL from generic PubChem prior ===")
run_reinvent("rl_ic50_generic_prior.toml", "rl_ic50_generic_prior.log", timeout=7200)

# ── Step 6: Sample from Plan D agent + generic prior ──
log("=== Plan D: Sampling from generic RL agent and generic prior ===")
# Generic RL agent sampling
sd_config = """run_type = "sampling"
[parameters]
model_file = \"""" + ROOT + """/models/saponin_ic50_generic.chkpt"
num_smiles = 15000
output_file = \"""" + ROOT + """/samples/ic50_generic_rl_agent_samples.csv"
unique_molecules = true
randomize_smiles = true
temperature = 1.0
isomeric_smiles = false"""
with open(f"{ROOT}/configs/sampling/ic50_generic_rl_sampling.toml", "w") as f:
    f.write(sd_config)
run_sampling("sampling/ic50_generic_rl_sampling.toml", "sampling/ic50_generic_rl_sampling.log", timeout=300)

# Generic prior (no RL) sampling
sd2_config = """run_type = "sampling"
[parameters]
model_file = \"""" + ROOT + """/priors/reinvent_pubchem.prior"
num_smiles = 10000
output_file = \"""" + ROOT + """/samples/ic50_generic_prior_samples.csv"
unique_molecules = true
randomize_smiles = true
temperature = 1.0
isomeric_smiles = false"""
with open(f"{ROOT}/configs/sampling/ic50_generic_prior_sampling.toml", "w") as f:
    f.write(sd2_config)
run_sampling("sampling/ic50_generic_prior_sampling.toml", "sampling/ic50_generic_prior_sampling.log", timeout=300)

# ── Step 7: Run unified analysis ──
log("=== All RL + sampling complete. Running unified analysis ===")
analysis_result = subprocess.run(
    [f"{ROOT}/venv/bin/python", f"{ROOT}/scripts/unified_analysis.py"],
    capture_output=True, text=True, timeout=3600,
    env={**ENV, "PATH": f"{ROOT}/venv/bin:{os.environ['PATH']}"}
)
print(analysis_result.stdout)
if analysis_result.stderr:
    print("STDERR:", analysis_result.stderr[:2000])

log("=== ALL DONE ===")