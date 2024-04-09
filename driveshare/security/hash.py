from hashlib import sha256, sha512, md5

class Hasher:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def hash(self, data: str) -> str:
        if self.algorithm == 'sha256':
            return sha256(data.encode()).hexdigest()
        elif self.algorithm == 'sha512':
            return sha512(data.encode()).hexdigest()
        elif self.algorithm == 'md5':
            return md5(data.encode()).hexdigest()
        else:
            raise ValueError("Invalid hashing algorithm")
        
    def verify(self, data: str, hashed: str) -> bool:
        return self.hash(data) == hashed

    