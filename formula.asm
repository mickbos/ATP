.cpu cortex-m0

.global compilertest 

compilertest:
	push {r7, lr}
	sub sp, sp, #8
	add r7, sp, #0
	str r0, [r7, #4]
	ldr r2, [r7, #4]
	add r2, r2, #1
	str r2, [r7, #4]
	ldr r2, [r7, #4]
	mov r0, r2
	mov sp, r7
	add sp, sp, #8
	pop {r7, pc}
