from sqlalchemy import bindparam
from pgvector.sqlalchemy import Vector
import numpy as np

DIM = 1536

def sa_bind_vector(name: str, value: list[float]):
    return bindparam(name, value=[float(x) for x in value], type_=Vector(DIM))

def sa_cosine_similarity_expr(column_vector, q_param):
    return (1 - column_vector.cosine_distance(q_param))

def np_cosine_similarity(a, b) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def np_cosine_similarity_batch(A, b):
    A = np.asarray(A, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    nb = np.linalg.norm(b)
    if nb == 0:
        return np.zeros(A.shape[0], dtype=np.float32)
    An = np.linalg.norm(A, axis=1)
    dots = A @ b
    denom = An * nb
    denom[denom == 0] = np.finfo(np.float32).eps
    return (dots / denom).astype(np.float32).tolist()
