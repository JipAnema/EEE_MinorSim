import time
production = 55
factor =  [0, 0],[3, 0],[3.5, 36],[4, 76],[4.5, 134],[5, 192],[5.5, 269],[6, 346],[6.5, 465],[7, 584],[7.5, 737],[8, 890],[8.5, 1098],[9, 1306],[9.5, 205],[10, 475],[10.5, 896],[11, 486],[11.5, 937],[12, 84],[12.5, 617],[13, 851],[13.5, 887],\
[14, 997],[14.5, 137],[15, 337],[15.5, 370],[25, 752],[25.5, 959],[35, 863],[35.5, 710],[36, 523],[36.5, 802],[37, 61],[37.5, 944],[38, 411],[38.5, 299],[39, 270],[39.5, 239],[40, 13],[40.5, 169],[41, 873],[41.5, 880],[42, 348],[42.5, 843],\
[43, 373],[43.5, 260],[44, 645],[44.5, 979],[45, 248],[45.5, 344],[46, 973],[46.5, 596],[47, 96],[47.5, 178],[48, 441],[48.5, 897],[49, 780],[49.5, 819],[50, 720],[50.5, 216],[51, 191],[51.5, 257],[52, 215],[52.5, 474],[53, 690],[53.5, 585],\
[54, 201],[54.5, 962],[55, 812],[55.5, 132],[56, 410],[56.5, 969],[57, 619],[57.5, 773],[58, 96],[58.5, 836],[59, 686],[59.5, 849],[60, 377],[60.5, 78],[61, 907],[61.5, 875],[62, 985],[62.5, 814],[63, 438],[63.5, 736],[64, 166],[64.5, 988],\
[65, 858],[65.5, 946],[66, 491],[66.5, 583],[67, 889],[67.5, 779],[68, 348],[68.5, 532],[69, 679],[69.5, 41],[70, 493],[70.5, 788],[71, 956],[71.5, 920],[72, 586],[72.5, 986],[73, 53],[73.5, 588],[74, 442],[74.5, 557],[75, 777],[75.5, 188],\
[76, 846],[76.5, 893],[77, 806]          # 2D list to convert m/s to kW for Wind system
            #0      1       2       3       4           5       6           7       8           9       10          11      12          13          14          15          16          17          18          19          20          21          22          23          24          25          26          27          28      29   

starttime = time.perf_counter()
# O(log n)
length = len(factor)
upperFind = length
lowerFind = 0
tryindex = int(upperFind / 2)

count = 0

for i in range(production):
    if i >= factor[upperFind - 1][0]:
        upperFind -= 1
        lowerFind = upperFind - 1
    elif i <= factor[lowerFind][0]:
        upperFind = 1
    else:
        while upperFind - lowerFind != 1:
            tryval = factor[tryindex][0]
            if i > tryval:
                lowerFind = tryindex
                tryindex += int((upperFind - lowerFind) / 2)
            elif i < tryval:
                upperFind = tryindex
                tryindex -= int((upperFind - lowerFind) / 2)
            else:
                upperFind = tryindex + 1
                lowerFind = tryindex
    count += 1
endtime = time.perf_counter()
print ("beter:")
print (count)
print (factor[upperFind][0])
print (factor[lowerFind][0])
print (starttime - endtime)

starttime = time.perf_counter()
# O(n)
        # Find index for interpolation
for j in range(production):
    for i in range(len(factor)):
        if j < factor[i][0]:
            index = i
            break
    else:
        index = len(factor) - 1
    count += 1

endtime = time.perf_counter()
print ("poopoo:")
print (count)
print (factor[index][0])
print (factor[index-1][0])
print (starttime - endtime)