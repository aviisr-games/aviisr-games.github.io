# pack_generator (legacy)

Note: `ninely/play/daily-pack.json` no longer comes from this tool. The pack is exported from the Ninely
app's own Daily by the Ninely pipeline (`Tools/WebDaily/run.sh <start yyyy-MM-dd> 400` in
aviisr-games/Ninely: one engine, every day validated with an independent oracle, reproducible sha256,
tier ramp equal to the app). Running this generator again would put boards in the pack that differ from
the app's Daily. It is kept for reference only; do not use it to regenerate the pack.
