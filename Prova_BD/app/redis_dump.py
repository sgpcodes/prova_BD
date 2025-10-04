import os
import json
import redis
from models import MessageIn, MessageOut

# ______________________________________________________________________________________________________

def read_value(r: redis.Redis, key: str, t: str):
    """
    Lê o valor da chave no Redis de acordo com seu tipo.
    """
    if t == "string":
        return r.get(key)
    if t == "hash":
        return r.hgetall(key)
    if t == "list":
        return r.lrange(key, 0, -1)
    if t == "set":
        return sorted(r.smembers(key))
    if t == "zset":
        return r.zrange(key, 0, -1, withscores=True)
    if t == "stream":
        return r.xrange(key, min="-", max="+", count=100)
    return f"<tipo '{t}' não tratado>"

# ______________________________________________________________________________________________________

def main():
    """
    Conecta ao Redis, lê todas as chaves usando SCAN, coleta seus dados
    (tipo, TTL, valor) e imprime um dump JSON formatado.
    """
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    password = os.getenv("REDIS_PASSWORD")

    r = redis.Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True  # Retorna strings ao invés de bytes
    )

    dump = {}

    # Itera com SCAN para evitar travar o servidor em bases grandes
    for key in r.scan_iter(match="*", count=200):
        t = r.type(key)
        ttl = r.ttl(key)
        dump[key] = {
            "type": t,
            "ttl": ttl,
            "value": read_value(r, key, t),
        }

    # Imprime JSON legível com indentação e suportando caracteres UTF-8
    print(json.dumps(dump, ensure_ascii=False, indent=2))

# ______________________________________________________________________________________________________

if __name__ == "__main__":
    main()