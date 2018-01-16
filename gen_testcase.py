FILESIZE = 1024* 1024 * 16
FILENAME = "testcase/a7"

with open(FILENAME, "a") as fout:
    fout.write('a' * 1024 * 1024)
    fout.write('b' * 1024 * 1024)
    fout.write('c' * 1024 * 1024)
    fout.write('a' * 1024 * 1024)
    fout.write('d' * 1024 * 1024)
    fout.write('b' * 1024 * 1024)
    fout.write('e' * 1024 * 1024)
    fout.write('d' * 1024 * 1024)
    fout.write('c' * 1024 * 1024)
    fout.write('1' * 1024 * 1024)
    fout.write('5' * 1024 * 1024)
    fout.write('8' * 1024 * 1024)
    fout.write('z' * 1024 * 1024)
    fout.write('g' * 1024 * 1024)
    fout.write('q' * 1024 * 1024)
    fout.write('9' * 1024 * 1024)
