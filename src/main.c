#include "main.h"
#include "core.h"
int main()
{
    ldi(2,-127);
    ldi(3,-127);
    add(1,2,3);
    printRF();
    return 0;
}
