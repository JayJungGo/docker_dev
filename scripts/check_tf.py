import time
import tensorflow as tf

print("[tf] self-test start")
print("TF:", tf.__version__)

gpus = tf.config.list_physical_devices("GPU")
print("GPUs:", gpus)

if not gpus:
    raise SystemExit("[tf] No GPU visible")

for g in gpus:
    try:
        tf.config.experimental.set_memory_growth(g, True)
    except Exception:
        pass

a = tf.random.normal([2048, 2048])
b = tf.random.normal([2048, 2048])

t0 = time.time()
c = tf.matmul(a, b)
_ = c.numpy()
print("[tf] Matmul OK, ms:", round(1000*(time.time()-t0), 2))
print("[tf] OK")
