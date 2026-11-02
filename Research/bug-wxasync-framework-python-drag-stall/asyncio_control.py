"""Control: is asyncio itself punctual? (no wx involved)

On every interpreter tested this reports ~47-50 wakes/second with a worst case of a few
tens of ms - i.e. asyncio.sleep(0.02) is NOT the problem. Included so the bug report can
show that control up front.

Run: python asyncio_control.py
"""
import asyncio
import statistics
import sys
import time


async def main():
    gaps = []
    last = time.perf_counter()
    for _ in range(300):                     # ~6 s at 50 Hz
        await asyncio.sleep(0.02)
        now = time.perf_counter()
        gaps.append((now - last) * 1000.0)
        last = now
    gaps = gaps[10:]                         # skip warmup
    s = sorted(gaps)
    print("python %s framework=%r" % (sys.version.split()[0], repr(getattr(sys, "_framework", None))))
    print("n=%d median=%.1fms mean=%.1fms p95=%.1fms max=%.1fms over_100ms=%d effective=%.1f/s"
          % (len(gaps), statistics.median(gaps), statistics.mean(gaps),
             s[int(len(gaps) * 0.95)], max(gaps), sum(1 for g in gaps if g > 100),
             1000.0 / statistics.mean(gaps)))


if __name__ == "__main__":
    asyncio.run(main())
