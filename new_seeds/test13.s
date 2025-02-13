.section .text
.global _start

_start:
    li a0, 5
    li a1, 3
    add a0, a0, a1

    li a2, 7

    bgt a0, a2, bigger_than_a2

    addi a0, a0, 2

    j skip_block

bigger_than_a2:
    sub a0, a0, a2

skip_block:
    
    la t0, tohost
    sw a0, 0(t0)

    
    li a0, 9
    la t1, fromhost
    sw a0, 0(t1)

1:
    j 1b


.section .tohost,"aw",@progbits
.align 8
.globl tohost
tohost:
    .dword 0

.section .fromhost,"aw",@progbits
.align 8
.globl fromhost
fromhost:
    .dword 0
