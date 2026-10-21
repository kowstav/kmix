import struct
import numpy as np
MAGIC=b"FX2TFW01"
DTYPE_INT8=0
DTYPE_BF16_BITS=1
DTYPE_FLOAT32=2
DTYPE_INT32=3
_DTYPE_TO_NUMPY={0:np.int8,1:np.uint16,2:np.float32,3:np.int32}
def write_tensor_file(
    filename: str, entries: list[tuple[str, int, np.ndarray]]
) -> None:
    with open(filename, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<I", len(entries)))
        for name, dtype_code, array in entries:
            assert array.dtype == _DTYPE_TO_NUMPY[dtype_code], name
            data = np.ascontiguousarray(array)
            encoded = name.encode()
            f.write(struct.pack("<I", len(encoded)))
            f.write(encoded)
            f.write(struct.pack("<B", dtype_code))
            f.write(struct.pack("<I", data.ndim))
            f.write(struct.pack(f"<{data.ndim}I", *data.shape))
            f.write(data.tobytes())

def read_tensor_file(filename: str) -> dict[str, tuple[int, np.ndarray]]:
    with open(filename, "rb") as f:
        assert f.read(8) == MAGIC
        (n_tensors,) = struct.unpack("<I", f.read(4))
        tensors: dict[str, tuple[int, np.ndarray]] = {}
        for _ in range(n_tensors):
            (name_length,) = struct.unpack("<I", f.read(4))
            name = f.read(name_length).decode()
            (dtype_code,) = struct.unpack("<B", f.read(1))
            (ndim,) = struct.unpack("<I", f.read(4))
            shape = struct.unpack(f"<{ndim}I", f.read(4 * ndim))
            dtype = np.dtype(_DTYPE_TO_NUMPY[dtype_code])
            count = int(np.prod(shape))
            array = np.frombuffer(
                f.read(count * dtype.itemsize), dtype=dtype
            ).reshape(shape)
            assert name not in tensors
            tensors[name] = (dtype_code, array)
        assert f.read(1) == b""
        return tensors
