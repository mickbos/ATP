.cpu cortex-m0

.global even 
.global odd 
even:
	push {r7, lr}
	sub sp, sp, #16
	add r7, sp, #0
	str r0, [r7, #4]
	ldr r2, [r7, #4]
	mov r3, #0
	cmp r2, r3
	bne .L1
	mov r0, #1
	b .L2
.L1:
	ldr r2, [r7, #4]
	mov r3, #1
	sub r2, r2, r3
	mov r0, r2
	bl odd
	mov r0, r0
.L2:
	mov sp, r7
	add sp, sp, #16
	pop {r7, pc}
odd:
	push {r7, lr}
	sub sp, sp, #16
	add r7, sp, #0
	str r0, [r7, #4]
	ldr r2, [r7, #4]
	mov r3, #0
	cmp r2, r3
	bne .L3
	mov r0, #0
	b .L4
.L3:
	ldr r2, [r7, #4]
	mov r3, #1
	sub r2, r2, r3
	mov r0, r2
	bl even
	mov r0, r0
.L4:
	mov sp, r7
	add sp, sp, #16
	pop {r7, pc}
