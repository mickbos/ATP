.cpu cortex-m0

.global sommig 
sommig:
	push {r7, lr}
	sub sp, sp, #8
	add r7, sp, #0
	str r0, [r7, #4]
	str r2, [r7, #8]
.L1
	ldr r2, [r7, #4]
	cmp r2, #0
	bg .L1
	ldr r2, [r7, #8]
	ldr r3, [r7, #4]
	add r2, r2, r3
	str r2, [r7, #8]
	ldr r2, [r7, #4]
	sub r2, r2, #1
	str r2, [r7, #4]
.L2
	ldr r2, [r7, #8]
	mov r0, r2
	mov sp, r7
	add sp, sp, #8
	pop {r7, pc}
