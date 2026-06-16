# scripts/check_torch.py
import time, torch
print("[torch] self-test start")
print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if not torch.cuda.is_available():
    raise SystemExit(1)
print("Capability:", torch.cuda.get_device_capability())
print("Device:", torch.cuda.get_device_name(0))

# GEMM sanity
x = torch.randn(4096, 4096, device="cuda")
y = torch.randn(4096, 4096, device="cuda")
torch.cuda.synchronize(); t0 = time.time()
z = x @ y
torch.cuda.synchronize()
print("GEMM OK, shape:", tuple(z.shape), "ms:", round(1000*(time.time()-t0), 2))

# quick backprop
lin = torch.nn.Linear(1024, 1024).cuda()
opt = torch.optim.Adam(lin.parameters(), lr=1e-3)
batch = torch.randn(32, 1024, device="cuda")
for _ in range(3):
    opt.zero_grad(set_to_none=True)
    loss = lin(batch).pow(2).mean()
    loss.backward()
    opt.step()
print("[torch] Backprop OK")
print("[torch] OK")

