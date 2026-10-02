* Lidar receiving method

lidar's receiving speed is very fast, and received data are in data buffer( on teensy ). there is also a problem that received data may not be in the right sequence, for example:

1 degree and 1distance, 2 degree and 2distance, 6 degree and 6distance, 3 degree and 3distance...  data may jump.

we can use a distance array and index to store the distance data in the sequence of angles

when we receive a lidar's data, it's in this form: 1 byte quality, 2 bytes angle, 2 bytes distance

then we use the angle to be the index ( should be convert to 'int' ), and store the distance ( 'float' ) in the array of this index

this can solve the problem of missing data and data jumping, in the last example, the diatance array would be:

array\[1]=1distance

array\[2]=2distance

array\[3]=3distance

array\[4]=0

array\[5]=0

array\[6]=6distance

if we store the data just by the sequence we received, than missing data would change the whole dataset and may influence the next dataset



* bluetooth

the appropriate baud for our bluetooth module HC-05 is 9600. previously, we set this to 115200, and it caused a delay about 1-2 seconds, it's really hard to find out why.

