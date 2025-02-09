.section .text
.global _start

_start:
    li a0, 10
    li a1, 1
    
    beq a0, a1, cond_equal

    addi a1, a1, 5

    j middle_block

cond_equal:
    addi a0, a0, -3

middle_block:
    bne a0, a1, second_check

    sll a0, a0, a1

second_check:
    la t0, tohost
    sw a0, 0(t0)

1:
    j 1b

.section .tohost,"aw",@progbits
.align 8
.globl tohost
tohost:
    .dword 0
