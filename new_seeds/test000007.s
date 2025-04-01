.section .text
.global _start

_start:
    li a0, 10
    li a1, 5
    j L1

L3:
    add a0, a0, a1
    j L2

L1:
    sub a0, a0, a1
    j L3

L2:
    
    xor a0, a0, a1
    j L4

L4:
    
    mul a0, a0, a1
    j done

done:
    la t0, tohost
    sw a0, 0(t0)

    la t1, fromhost
    sw a1, 0(t1)

loop_end:
    j loop_end

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
