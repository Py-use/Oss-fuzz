.section .text
.global _start

_start:
    li a0, 2
    li a1, 2
    mul a0, a0, a1

    li a2, 4
    beq a0, a2, skip_block

    sub a0, a0, a1

skip_block:
    
    la t0, tohost
    sw a0, 0(t0)

    li a0, 9
    la t1, fromhost
    sw a0, 0(t1)

    j .

.section .tohost, "aw", @progbits
.align 8
.globl tohost
tohost:
    .dword 0

.section .fromhost, "aw", @progbits
.align 8
.globl fromhost
fromhost:
    .dword 0
