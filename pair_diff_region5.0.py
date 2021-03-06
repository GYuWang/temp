import numpy as np
from itertools import combinations
from sklearn import linear_model
from scipy import stats
import matplotlib.pyplot as plt


def region_detect(TAD1, TAD2):
    flag1 = []
    flag2 = []
    band_s = np.array([0,0,0])
    for i in range(0,TAD1.shape[0]):
        for j in range(0, TAD2.shape[0]):
            if abs(TAD1[i,2] - TAD2[j,2]) <= 10 and abs(TAD1[i,1] - TAD2[j,1]) <= 10:
                band_s = np.vstack([band_s, (TAD1[i,:]+TAD2[j,:])/2])
                flag1.append(i)
                flag2.append(j)
    TAD1_only = np.delete(TAD1, flag1, axis=0)
    TAD2_only = np.delete(TAD2, flag2, axis=0)
    return band_s[1:,:], TAD1_only, TAD2_only


def sim_range(TAD):
    r = []
    for t in TAD:
        r1 = (t[8] - t[7] + t[5] - t[4])/(t[2] - t[1])
        r.append(r1)

    r = np.array(r)
    r = r.reshape(r.shape[0], 1)
    TAD = np.concatenate((TAD, r), 1)
    return TAD



def RangInList(L, TAD):
    flag1 = 1
    for t in TAD:
        if abs(L[1] - t[1]) < 10 and abs(L[2] - t[2]) < 10:
            flag1 = 0
    return flag1



def TAD_divid_V3(range1, range2, TAD_s):
    flag = 0
    for t in range2:
        if abs(t[1] - range1[1]) < 10:
            flag = flag + 1
        if abs(t[2] - range1[2]) < 10:
            flag = flag + 1
    if flag >= 2:
        #f = RangInList(range1, TAD_s.tolist())  # remove similar large region
        #print(range1)
        #if f == 1:
        dic = []
        for i in range(2, range2.shape[0] + 1):
            comb = list(combinations(range(range2.shape[0]), i))
            for j, t in enumerate(comb):
                x = range2[t, :]
                length = 0
                flag3 = []                                                  # all divide region are similar region
                for s in x:
                    length = length + s[2] - s[1]
                    f2 = RangInList(s, TAD_s.tolist())
                    flag3.append(f2)

                r = length / (range1[2] - range1[1])
                #print(x, r, sum(flag3))
                #if r > 0.9 and r < 1.1 and sum(flag3) != 0:
                if r > 0.9 and r < 1.1:                                     # not need to remove similar region
                    flag2 = 0  # find all real sep
                    for l in range(x.shape[0]-1):
                        print(x[l, :], x.shape[0])
                        if x[l + 1, 1] - x[l, 2] > 30 or x[l, 2] - x[l + 1, 1] > 20:
                            flag2 = 1
                    if flag2 == 0:
                        dic.append([x, r])
                        # print(x, r)
        return(dic)




def region_divid_v3(TAD1, TAD2, TAD_s):
    '''
    :param TAD1: whole region
    :param TAD2: divide region
    :param TAD_s: similar region
    :return: D1: TAD of unit region, D2: divide TAD with coverage rate, D3: divide TAD without coverage rate
    '''
    TAD_in = np.empty(shape = [0, 3])
    diff1 = []
    diff2 = []
    diff3 = []
    count = 0
    for i, t1 in enumerate(TAD1):
        for t2 in TAD2:
            if t1[1] - t2[1] < 20 and t2[2] - t1[2] < 20:
                TAD_in = np.append(TAD_in, [t2], axis=0)
        #print(t1, TAD_in)                        # cannot find region????
        D = TAD_divid_V3(t1, TAD_in, TAD_s)
        print(t1, D)
        if D is not None and len(D) != 0:
            #dif.append([t1, D])
            m = []
            for j in range(0, len(D)):
                m.append(D[j][0].shape[0])
            #print(t1, D, max(m))

            for j in range(0, len(D)):
                if D[j][0].shape[0] == max(m):
                    diff1.append([t1, count])
                    diff2.append(D[j])
                    diff3.append([D[j][0][:, 1:3], count])
                    count = count + 1
                    max_region = D[j]
            #print(t1, max_region[0][:, 1:3])
        TAD_in = np.empty(shape=[0, 3])
    return np.array(diff1), np.array(diff2), np.array(diff3)



###### find divide regions

def linear_transform(map, left, right, up, down):
    '''
    use linear regression to transform matrix
    :param map: contact map
    :return: transformed contact map in left-right, up-down
    '''
    x = np.empty(shape=[1])
    y = np.empty(shape=[1])
    for i in range(up, down):
        dig = max(left, i)
        for j in range(dig, right):
            if map[i, j] != 0 and (j-i) > 2:
                x = np.append(x, np.log(j-i))
                y = np.append(y, np.log(map[i, j]))
    x = x.reshape(x.shape[0], 1)
    y = y.reshape(y.shape[0], 1)
    regr = linear_model.LinearRegression()
    regr.fit(x, y)
    pred = regr.predict(x)
    m = regr.coef_[0]
    b = regr.intercept_

    # fig, ax = plt.subplots()
    # ax.scatter(x,y)
    # ax.plot(x, pred, color='blue', linewidth=3)
    # plt.show()
    # print(m, b)
    return m, b




def linear_transform_plot(map, left, right, up, down):
    '''
    use linear regression to transform matrix
    :param map: contact map
    :return: transformed contact map in left-right, up-down
    '''
    x = np.empty(shape=[1])
    y = np.empty(shape=[1])
    for i in range(up, down):
        # dig = max(left, i)
        for j in range(left, right):
            if map[i, j] != 0 and (j-i) > 2:
                x = np.append(x, np.log(j-i))
                y = np.append(y, np.log(map[i, j]))
    x = x.reshape(x.shape[0], 1)
    y = y.reshape(y.shape[0], 1)
    regr = linear_model.LinearRegression()
    regr.fit(x, y)
    pred = regr.predict(x)
    m = regr.coef_[0]
    b = regr.intercept_

    print(left)
    print(up)
    #print(map.shape)
    print(x)
    print(y)
    # fig, ax = plt.subplots()
    # ax.scatter(x,y)
    # ax.plot(x, pred, color='blue', linewidth=3)
    # plt.show()
    # print(m, b)

    return m, b




def calculate_region_mean(D3, map1, map2, p1, p2):
    '''
    :param D3: divided region
    :param map1: contact map of cell1
    :param map2: contact map of cell2
    :return: average interaction between different divided region
    '''
    avr_all1 = []
    avr_all2 = []
    avr_diff = []
    for count, d0 in enumerate(D3):
        d = d0[0]
        avr_all1_temp = np.empty(shape=[d.shape[0], d.shape[0]])
        avr_all2_temp = np.empty(shape=[d.shape[0], d.shape[0]])
        for i in range(d.shape[0]):
            for j in range(d.shape[0]):
                m1 = map1[int(d[i][0]): int(d[i][1]), int(d[j][0]): int(d[j][1])]
                m2 = map2[int(d[i][0]): int(d[i][1]), int(d[j][0]): int(d[j][1])]

                slope1, b1 = linear_transform(map1, int(d[i][0]), int(d[i][1]), int(d[j][0]), int(d[j][1]))
                #avr1 = np.mean(m1[m1 < p1])             # need to change!!!!
                avr_all1_temp[i, j] = b1
                slope2, b2 = linear_transform(map2, int(d[i][0]), int(d[i][1]), int(d[j][0]), int(d[j][1]))
                #avr2 = np.mean(m2[m2 < p2])             # need to change!!!!
                avr_all2_temp[i, j] = b2
        avr_all1.append([avr_all1_temp, count])
        avr_all2.append([avr_all2_temp, count])
        avr_diff.append([avr_all1_temp - avr_all2_temp, count])

    print(avr_all1)
        # if count == 2:
        #     for i in range(d.shape[0]):
        #         for j in range(d.shape[0]):
        #             #print(map1[int(d[i][0]): int(d[i][1]), int(d[j][0]): int(d[j][1])])
        #             slope1, b1 = linear_transform_plot(map1, int(d[j][0]), int(d[j][1]), int(d[i][0]), int(d[i][1]))
        #             #
        #             # avr1 = np.mean(m1[m1 < p1])             # need to change!!!!
        #             #avr_all1_temp[i, j] = b1
        #             #slope2, b2 = linear_transform(map2, int(d[i][0]), int(d[i][1]), int(d[j][0]), int(d[j][1]))
        #             # avr2 = np.mean(m2[m2 < p2])             # need to change!!!!
        #             #avr_all2_temp[i, j] = b2

    return avr_all1, avr_all2, avr_diff






def calculate_region_split100(D3, map, n):
    '''
    split each region into n small region
    :param D3: divided region
    :param map1: contact map of cell1
    :param n: region number
    :return: average interaction between different divided region
    '''
    avr_all = np.empty(shape=(0, 3, 30, 30))
    for count, d0 in enumerate(D3):
        d = d0[0]
        for i in range(d.shape[0]-1):
            s1 = np.array_split(range(int(d[i][0]), int(d[i][1])), n)
            s2 = np.array_split(range(int(d[i+1][0]), int(d[i+1][1])), n)
            avr_all2_temp_1 = np.empty(shape=[n,n])
            avr_all2_temp_2 = np.empty(shape=[n, n])
            avr_all2_temp_3 = np.empty(shape=[n, n])
            for t1 in range(n):
                for t2 in range(n):
                    m = map[s1[t1][0]:(s1[t1][-1]+1), s1[t2][0]:(s1[t2][-1]+1)]
                    m[m > 10] = 10
                    avr1 = np.mean(m)
                    avr_all2_temp_1[t1, t2] = avr1
            for t1 in range(n):
                for t2 in range(n):
                    m = map[s1[t1][0]:(s1[t1][-1]+1), s2[t2][0]:(s2[t2][-1]+1)]
                    m[m > 10] = 10
                    avr1 = np.mean(m)
                    avr_all2_temp_2[t1, t2] = avr1
            for t1 in range(n):
                for t2 in range(n):
                    m = map[s2[t1][0]:(s2[t1][-1]+1), s2[t2][0]:(s2[t2][-1]+1)]
                    m[m > 10] = 10
                    avr1 = np.mean(m)
                    avr_all2_temp_3[t1, t2] = avr1
            #avr_all0_temp.append(np.array([avr_all2_temp_1,avr_all2_temp_2,avr_all2_temp_3]))
            #print(np.array([[avr_all2_temp_1, avr_all2_temp_2, avr_all2_temp_3]]).shape)
            #print(avr_all.shape)
            avr_all = np.append(avr_all, [[avr_all2_temp_1, avr_all2_temp_2, avr_all2_temp_3]], axis=0)
        #avr_all.append(np.array(avr_all0_temp))
    return avr_all



def count_cross_prob_eachregion(intract):
    R = np.zeros((intract.shape[0] - 1, intract.shape[0] - 1))
    for i in range(intract.shape[0] - 1):
        for j in range(intract.shape[0] - 1):
            R[i, j] = (intract[i, j + 1] * 2) / (intract[i, j] + intract[i + 1, j + 1])
            #print(i, j, R[i, j], intract[i, j + 1], intract[i, j], intract[i + 1, j + 1])
    return R


def count_cross_prob(avr):
    '''
    count the ratio of interaction in conner region/ interaction in diagonal region
    :param avr: mean of interaction in each region
    :return: matrix of ratio, flag == 1 is real merge region
    '''
    ratio = []
    for count, t in enumerate(avr):
        intract = t[0]
        R = count_cross_prob_eachregion(intract)
        x1 = R.diagonal()[R.diagonal() > 0.45].shape[0]   # high ratio region define by o.45 as cutoff
        x2 = R.diagonal()[R.diagonal() < 0.45].shape[0]   # low ratio region
        flag = 0
        if R.shape[0] == 1:
            if R[0, 0] > 0.45:
                flag = 1
        else:
            if x2 < x1:
                flag = 1
        ratio.append([R, count, flag])
    return ratio



def compar_prob(ratio1, ratio2):
    '''
    find real split site
    :param ratio1: split region
    :param ratio2: merge region
    :return: real split site
    '''
    idx = []
    for i in range(len(ratio1)):
        if ratio2[i][2] == 1 and ratio1[i][2] != 1:
            ratio_tmp = ratio2[i][0] - ratio1[i][0]
            if np.mean(ratio_tmp.diagonal()) > 0.09:    # real divide region by cutoff: -0.1
                idx.append(ratio2[i][1])
    return idx




def count_intrc(idx, avr):
    '''
    count average interaction
    :param idx: index of real region
    :param avr: interact of all region
    :return: average interaction
    '''
    inter = np.empty(shape=(0,3))
    for t in avr:
        if t[1] in idx:
            T = t[0]                    # interaction array
            for i in range(T.shape[0] - 1):
                inter_tmp = [T[i, i], T[i, i+1], T[i+1, i+1]]
                inter = np.append(inter, [inter_tmp], axis=0)
    return inter





def loc_divid(D3, idx):
    '''
    find the location of divide region
    :param D3: all divided region
    :param idx: real region
    :return: location of real region
    '''
    reg = np.empty(shape=(0,2))
    for d in D3:
        if d[1] in idx:
            reg = np.append(reg, d[0], axis=0)
    return reg





def loc_union(D1, idx):
    '''
    find the location of union region
    :param D3: all divided region
    :param idx: real region
    :return: location of real region
    '''
    reg = np.empty(shape=(0,3))
    for d in D1:
        if d[1] in idx:
            reg = np.append(reg, [d[0]], axis=0)
    return reg[:,1:3]





def remove_diff(loc_u, loc_d, TAD_s):
    '''
    remove differential region from similar region
    :param loc_u: TAD of union region
    :param loc_d: TAD of divide region
    :param TAD_s: TAD of similar region
    :return: similar region without differential region
    '''
    diff = np.append(loc_u, loc_d, axis=0)
    dlt = np.empty(shape=(0, 3))
    idx = []
    for i, t in enumerate(TAD_s):
        if min(abs(t[1] - diff[:, 1])) < 10 and min(abs(t[2] - diff[:, 2])) < 10:
            dlt = np.append(dlt, [t], axis=0)
            idx.append(i)
    TAD_s = np.delete(TAD_s, idx, 0)
    return TAD_s




def divid_region(f1, f2, D3, D1, TAD_s, p1, p2):
    '''
    main function for divided region detection
    :param f1: cell line1
    :param f2: cell line2
    :param D3: divided region in cell line 1
    :param D1: Unite region in cell line 2
    :param TAD_s: similar region
    :return: divid1: mean interaction in divide region, divid2: mean interaction in union region, loc_d: location of
    divided region, loc_u: location of union region, dlt: similar region after removing differential region
    '''
    map1 = np.loadtxt(f1)
    map2 = np.loadtxt(f2)
    avr1, avr2, avr_diff = calculate_region_mean(D3, map1, map2, p1, p2)      # count mean interaction in different region
    ratio1 = count_cross_prob(avr1)                                   # count diff ratio
    ratio2 = count_cross_prob(avr2)
    idx = compar_prob(ratio1, ratio2)                                 # find real divide region index
    if len(idx) > 0:
        divid1 = count_intrc(idx, avr1)                                 # count interaction in real divide region
        divid2 = count_intrc(idx, avr2)
        loc_u = loc_union(D1, idx)
        loc_u = np.insert(loc_u,0,  np.array(range(loc_u.shape[0])).transpose(), axis=1)
        loc_d = loc_divid(D3, idx)
        loc_d = np.insert(loc_d, 0, np.array(range(loc_d.shape[0])).transpose(), axis=1)
        dlt = remove_diff(loc_u, loc_d, TAD_s)
        return divid1, divid2, loc_d, loc_u, dlt
    else:
        return 0, 0, 0, 0, 0



# TAD1 = np.loadtxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HMEC/5_matrix_HMEC_Coverage_band.txt')
# TAD2 = np.loadtxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HUVEC/5_matrix_HUVEC_Coverage_band.txt')
# TAD_s, TAD1_only, TAD2_only = region_detect(TAD1, TAD2)
# D1, D2, D3 = region_divid_v3(TAD2, TAD1, TAD_s)
# f1 = "/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HMEC/5_matrix_HMEC_Coverage.txt"
# f2 = "/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HUVEC/5_matrix_HUVEC_Coverage.txt"
# divid1_1, divid2_1, loc_d, loc_u, dlt = divid_region(f1, f2, D3, D1, TAD_s)
#
# np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/chr5_divid.txt', divid1_1)
# np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/chr5_merge.txt', divid2_1)
# np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/chr5_divid_loc.txt', loc_d)
# np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/chr5_divid_union.txt', loc_u)
# np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/chr5_similar.txt', dlt)


def main_find_diff(chr):
    TAD2 = np.loadtxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HMEC/' + chr + '_matrix_HMEC_Coverage_band.txt')
    TAD1 = np.loadtxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HUVEC/' + chr + '_matrix_HUVEC_Coverage_band.txt')
    TAD_s, TAD1_only, TAD2_only = region_detect(TAD1, TAD2)
    D1, D2, D3 = region_divid_v3(TAD2, TAD1, TAD_s)

    # print('yyy')
    f2 = '/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HMEC/' + chr + '_matrix_HMEC_Coverage.txt'
    f1 = '/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HUVEC/' + chr + '_matrix_HUVEC_Coverage.txt'

    divid1_1, divid2_1, loc_d, loc_u, dlt = divid_region(f1, f2, D3, D1, TAD_s)

    try:
        if divid1_1 != 0:
            print('chr')
    except:
        np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/HMEC-HUVEC2/chr' + chr + '_divid.txt', divid1_1)
        np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/HMEC-HUVEC2/chr' + chr + '_merge.txt', divid2_1)
        np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/HMEC-HUVEC2/chr' + chr + '_divid_loc.txt', loc_d)
        np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/HMEC-HUVEC2/chr' + chr + '_divid_union.txt', loc_u)
        np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/HMEC-HUVEC2/chr' + chr + '_similar.txt', dlt)
        print(chr)




# for i in range(5,23):
#     print(i)
#     main_find_diff(str(i))



#main_find_diff('19')


TAD1 = np.loadtxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/IRM90/matrix/5_matrix_IMR90_Coverage.txt.4000.5000.band2.txt')
TAD2 = np.loadtxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HUVEC/5_matrix_HUVEC_Coverage.txt.4000.5000.band.txt')
TAD_s, TAD1_only, TAD2_only = region_detect(TAD1, TAD2)
D1, D2, D3 = region_divid_v3(TAD2, TAD1, TAD_s)

# print('yyy')
f1 = '/Users/guangyu/Work/Hi-C/Data/Contactmatrix/IRM90/matrix/5_matrix_IMR90_Coverage.txt.4000.5000'
f2 = '/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HUVEC/5_matrix_HUVEC_Coverage.txt.4000.5000'

divid1_1, divid2_1, loc_d, loc_u, dlt = divid_region(f1, f2, D3, D1, TAD_s, 25, 10)


try:
    if divid1_1 == 0:
        print('No')
except:
    np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/IMR90-HUVEC/5_divid.txt', divid1_1)
    np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/IMR90-HUVEC/5_merge.txt', divid2_1)
    np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/IMR90-HUVEC/5_divid_loc.txt', loc_d)
    np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/IMR90-HUVEC/5_divid_union.txt', loc_u)
    np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/IMR90-HUVEC/5_similar.txt', dlt)



# TAD1 = np.loadtxt('/Users/guangyu/Work/Hi-C/Data/nature12/chr4_chr4_matrix_band_0.85.txt')
# TAD2 = np.loadtxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HUVEC/4_matrix_HUVEC_Coverage_band.txt')
# TAD_s, TAD1_only, TAD2_only = region_detect(TAD1, TAD2)
# D1, D2, D3 = region_divid_v3(TAD2, TAD1, TAD_s)
#
# #print('yyy')
# f1 = '/Users/guangyu/Work/Hi-C/Data/nature12/chr4_chr4_matrix.txt'
# f2 = '/Users/guangyu/Work/Hi-C/Data/Contactmatrix/HUVEC/4_matrix_HUVEC_Coverage.txt'
#
# divid1_1, divid2_1, loc_d, loc_u, dlt = divid_region(f1, f2, D3, D1, TAD_s)
#
# try divid1_1 == 0:
#     np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/hESC/chr4_divid.txt', divid1_1)
#     np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/hESC/chr4_merge.txt', divid2_1)
#     np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/hESC/chr4_divid_loc.txt', loc_d)
#     np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/hESC/chr4_divid_union.txt', loc_u)
#     np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/hESC/chr4_similar.txt', dlt)
#     np.savetxt('/Users/guangyu/Work/Hi-C/Data/Contactmatrix/differential/hESC/chr4_similar_all.txt', TAD_s)
# except:
#     pass


