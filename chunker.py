class Chunker:
    def __init__(self, min=1024*1024-1, avg=1024*1024, max=2048*1024, mode='variable'):
        self.minChunkSize = min
        self.avgChunkSize = avg
        self.maxChunkSize = max
        self.windowSize = min
        self.mode = mode

    def _fix_size_chunking(self, bytes):
        byteSize = len(bytes)
        if byteSize <= self.avgChunkSize:
            return [byteSize]
        mutiple = byteSize // self.avgChunkSize
        return [self.avgChunkSize * mult for mult in range(1, mutiple + 1)]

    def _var_size_chunking(self, bytes):
        cuts = []
        byteSize = len(bytes)
        index, offset, max_b = 0, 0, -1
        if byteSize < self.windowSize:
            return [byteSize]
        while index < byteSize:
            if bytes[index] >= max_b:
                if index - offset + 1 > self.windowSize:
                    index += 1
                    cuts.append(index)
                    max_b = -1
                    offset = index
                else:
                    max_b = bytes[index]
            index += 1
        return cuts

    def chunking(self, bytes):
        if self.mode == 'variable':
            return self._var_size_chunking(bytes)
        else:
            return self._fix_size_chunking(bytes)

    def map_chunk(self, bytes, cuts, func, *args):
        offset = 0
        result = []
        for cut in cuts:
            result.append(func(bytes[offset:cut], *args))
            offset = cut
        if offset != len(bytes):
            result.append(func(bytes[offset:], *args))
        return result

    def divide_chunk(self, bytes, cuts):
        offset = 0
        for cut in cuts:
            yield bytes[offset:cut]
            offset = cut
        if offset != len(bytes):
            yield bytes[offset:]
