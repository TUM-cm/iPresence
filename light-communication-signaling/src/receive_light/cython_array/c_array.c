#include <string.h> // mem functions: copy, set
#include <stdio.h>

int a = 0;

void c_set_array (int* voltage, int volt_shape, unsigned int* time, int time_shape)
{
	printf("val: %d\n", a);
	memset(voltage, a, sizeof(voltage[0]) * volt_shape);
	memset(time, a, sizeof(time[0]) * time_shape);
	a++;
    return;
}

void c_copy_array (int* voltage, int volt_shape, unsigned int* time, int time_shape)
{
	int *data_volt;
	unsigned int *data_time;
	int i;

	//printf("volt shape: %d\n", volt_shape);
	//printf("time shape: %d\n", time_shape);

	data_volt = malloc(volt_shape * sizeof(int));
	data_time = malloc(time_shape * sizeof(unsigned int));
	for (i = 0; i < volt_shape; i++) {
		data_volt[i] = 100;
		//printf("%d\n", data_volt[i]);
	}
	for (i = 0; i < time_shape; i++) {
		data_time[i] = 300;
		//printf("%d\n", data_time[i]);
	}

	memcpy(voltage, data_volt, volt_shape * sizeof(int));
	memcpy(time, data_time, time_shape * sizeof(unsigned int));

	//memcpy(array, fill_array, array_shape * sizeof(int));

    return;
}
