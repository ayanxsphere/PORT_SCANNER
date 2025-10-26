
import socket, argparse, time
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_one(target, port, timeout):
    try:
        with socket.create_connection((target, port), timeout=timeout) as s:
            s.settimeout(timeout)                     # ensure recv respects timeout
            try:
                b = s.recv(512).decode(errors='ignore').strip()
            except Exception:
                b = ''
            return port, True, b
    except Exception:
        return port, False, ''

def main():
    p = argparse.ArgumentParser(description="Tiny threaded TCP connect scanner (polished)")
    p.add_argument("target")
    p.add_argument("start", type=int)
    p.add_argument("end", type=int)
    p.add_argument("--threads", type=int, default=100)
    p.add_argument("--timeout", type=float, default=0.8)
    args = p.parse_args()

    ports = range(max(1, args.start), min(65535, args.end) + 1)
    open_ports = []
    t0 = time.time()
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as ex:
            futures = [ex.submit(scan_one, args.target, port, args.timeout) for port in ports]
            for fut in as_completed(futures):
                port, ok, banner = fut.result()
                if ok:
                    open_ports.append((port, banner))
                    print(f"[+] {port}/tcp OPEN {'('+banner+')' if banner else ''}")
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user — exiting early.")
    print(f"Done in {time.time()-t0:.2f}s — found {len(open_ports)} open ports.")

if __name__ == "__main__":
    main()
