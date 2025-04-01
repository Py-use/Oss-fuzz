.section .text
.global _start

_start:
    li s7, 0xfffff
    li s6, 3
    sub s7, s7, s6

    
    la t0, tohost
    sw s7, 0(t0)

    
    li s7, 1
    sw s7, 0(t0)

    
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
