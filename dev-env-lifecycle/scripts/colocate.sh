#!/usr/bin/env bash
# colocate.sh — protect PROD_SLICE (containers) from best-effort DEV_SLICE (agents) on a cgroup-v2 systemd host.
# usage: colocate.sh apply [--with-tools] | status | revert   sizes: defaults below, overridden by env or $COLOCATE_ENV
set -euo pipefail
ENV_FILE="${COLOCATE_ENV:-/etc/colocate.env}"; [ -f "$ENV_FILE" ] && . "$ENV_FILE"
PROD_SLICE=${PROD_SLICE:-system.slice}; DEV_SLICE=${DEV_SLICE:-user.slice}; USER_SVC=${USER_SVC:-user@.service}
PROD_MEM_LOW=${PROD_MEM_LOW:-32G}; DEV_CPU_WEIGHT=${DEV_CPU_WEIGHT:-40}; DEV_MEM_HIGH=${DEV_MEM_HIGH:-80G}; DEV_MEM_MAX=${DEV_MEM_MAX:-96G}
DEV_IO_WEIGHT=${DEV_IO_WEIGHT:-50}; DEV_TASKS_MAX=${DEV_TASKS_MAX:-16384}; OOMD_LIMIT=${OOMD_LIMIT:-50%}; OOMD_DURATION=${OOMD_DURATION:-20s}
INOTIFY_INSTANCES=${INOTIFY_INSTANCES:-1024}; INOTIFY_WATCHES=${INOTIFY_WATCHES:-1048576}; TOOLS=${TOOLS:-"systemd-oomd iotop fd-find"}
D=/etc/systemd/system; SYSCTL=/etc/sysctl.d/60-colocate.conf; CG=/sys/fs/cgroup; OOMD_PREV=$D/.colocate-oomd-prev
[ -f $CG/cgroup.controllers ] || { echo "cgroup v2 required" >&2; exit 2; }
need_root() { [ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 2; }; }
dropin() { mkdir -p "$D/$1.d"; printf '[%s]\n%s\n' "$2" "$3" >"$D/$1.d/50-colocate.conf"; }
live() { systemctl set-property --runtime "$@"; }
user_svcs() { systemctl list-units --plain --no-legend 'user@*.service' | awk '{print $1}'; }
apply() {
  need_root; dropin "$PROD_SLICE" Slice "MemoryLow=$PROD_MEM_LOW"
  dropin "$DEV_SLICE" Slice "$(printf 'CPUWeight=%s\nMemoryHigh=%s\nMemoryMax=%s\nIOWeight=%s\nTasksMax=%s' \
    "$DEV_CPU_WEIGHT" "$DEV_MEM_HIGH" "$DEV_MEM_MAX" "$DEV_IO_WEIGHT" "$DEV_TASKS_MAX")"
  dropin "$USER_SVC" Service "$(printf 'ManagedOOMSwap=kill\nManagedOOMMemoryPressure=kill\nManagedOOMMemoryPressureLimit=%s\nManagedOOMMemoryPressureDurationSec=%s' \
    "$OOMD_LIMIT" "$OOMD_DURATION")"
  grep -qs '^# prev instances=' $SYSCTL || printf '# prev instances=%s watches=%s\n' "$(sysctl -n fs.inotify.max_user_instances)" "$(sysctl -n fs.inotify.max_user_watches)" >$SYSCTL
  { sed -n '1p' $SYSCTL; printf 'fs.inotify.max_user_instances = %s\nfs.inotify.max_user_watches = %s\n' "$INOTIFY_INSTANCES" "$INOTIFY_WATCHES"; } >$SYSCTL.tmp && mv $SYSCTL.tmp $SYSCTL
  systemctl daemon-reload; sysctl -q -p $SYSCTL
  live "$PROD_SLICE" MemoryLow="$PROD_MEM_LOW"
  live "$DEV_SLICE" CPUWeight="$DEV_CPU_WEIGHT" MemoryHigh="$DEV_MEM_HIGH" MemoryMax="$DEV_MEM_MAX" IOWeight="$DEV_IO_WEIGHT" TasksMax="$DEV_TASKS_MAX"
  for u in $(user_svcs); do live "$u" ManagedOOMSwap=kill ManagedOOMMemoryPressure=kill ManagedOOMMemoryPressureLimit="$OOMD_LIMIT" ManagedOOMMemoryPressureDurationSec="$OOMD_DURATION"; done
  [ -f $OOMD_PREV ] || systemctl is-enabled systemd-oomd.service >$OOMD_PREV 2>/dev/null || true
  if [ "${1:-}" = --with-tools ]; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y $TOOLS || echo "tools install failed; limits are applied, rerun apply --with-tools" >&2
  fi
  if systemctl cat systemd-oomd.service >/dev/null 2>&1; then systemctl enable --now systemd-oomd.service; else echo "NOTE: systemd-oomd absent — rerun with --with-tools"; fi
  status
}
status() {
  echo "$PROD_SLICE memory.low=$(cat $CG/$PROD_SLICE/memory.low) memory.current=$(cat $CG/$PROD_SLICE/memory.current)"
  echo "$DEV_SLICE cpu.weight=$(cat $CG/$DEV_SLICE/cpu.weight) memory.high=$(cat $CG/$DEV_SLICE/memory.high) memory.max=$(cat $CG/$DEV_SLICE/memory.max) io.weight=$(cat $CG/$DEV_SLICE/io.weight) pids.max=$(cat $CG/$DEV_SLICE/pids.max) memory.current=$(cat $CG/$DEV_SLICE/memory.current)"
  for u in $(user_svcs); do echo "$u $(systemctl show "$u" -p ManagedOOMMemoryPressure -p ManagedOOMMemoryPressureLimit | tr '\n' ' ')"; done
  echo "oomd=$(systemctl is-active systemd-oomd 2>/dev/null || true) swapkill=$(systemctl show "$(user_svcs | head -1)" -p ManagedOOMSwap --value) inotify=$(sysctl -n fs.inotify.max_user_instances)/$(sysctl -n fs.inotify.max_user_watches)"
  echo "psi: cpu $(head -1 /proc/pressure/cpu) | mem $(sed -n 2p /proc/pressure/memory) | $DEV_SLICE mem $(sed -n 2p $CG/$DEV_SLICE/memory.pressure)"
}
revert() {
  need_root; rm -f "$D/$PROD_SLICE.d/50-colocate.conf" "$D/$DEV_SLICE.d/50-colocate.conf" "$D/$USER_SVC.d/50-colocate.conf"
  if grep -qs '^# prev instances=' $SYSCTL; then read -r _ _ pi pw <$SYSCTL; sysctl -q -w "fs.inotify.max_user_instances=${pi#instances=}" "fs.inotify.max_user_watches=${pw#watches=}"; fi
  systemctl daemon-reload
  live "$PROD_SLICE" MemoryLow=0
  live "$DEV_SLICE" CPUWeight=100 MemoryHigh=infinity MemoryMax=infinity IOWeight=100 TasksMax=infinity
  for u in $(user_svcs); do live "$u" ManagedOOMSwap=auto ManagedOOMMemoryPressure=auto; done
  if [ "$(cat $OOMD_PREV 2>/dev/null)" != enabled ]; then systemctl disable --now systemd-oomd.socket systemd-oomd.service 2>/dev/null || true; fi
  rm -f $SYSCTL $OOMD_PREV
  status
}
case "${1:-}" in apply) apply "${2:-}";; status) status;; revert) revert;; *) echo "usage: $0 apply [--with-tools] | status | revert" >&2; exit 2;; esac
