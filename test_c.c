int sommar(int a) {
    if (a == 0) {
        return 0;
    }
    return sommar(a-1)+a;
}

void main() {
    int a = 10;
    int res = sommar(a);
}

