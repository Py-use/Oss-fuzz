.section .text
.global _start

_start:
    li a0, 5
    li a1, 3
    add a0, a0, a1

    
    la t0, tohost
    sw a0, 0(t0)

    
    li a0, 1
    sw a0, 0(t0)

    
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
