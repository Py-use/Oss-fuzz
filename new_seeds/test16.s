.section .text
.global _start

_start:
    li a0, 5
    li a1, 7

    add a0, a0, a1

    li a2, 10
    bgt a0, a2, label1

    addi a0, a0, 3
    j end_label

label1:
    sub a0, a0, a2

end_label:
    la t0, tohost
    sw a0, 0(t0)

1:
    j 1b

.section .tohost, "aw", @progbits
.align 8
.globl tohost
tohost:
    .dword 0
