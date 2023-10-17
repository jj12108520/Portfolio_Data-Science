import pandas as pd
import datetime
import numpy as np
from haversine import haversine


class SV30Preprocess:
    def __init__(self):
        pass
    '''
    A ship filtering
    '''
    def Aship_to_dict(self, df):
        start_a_ship = df[df.SHIP_CODE.str.startswith('A')].SHIP_CODE.unique()

        # key 값을 어선 종류, value 값을 해당 어선의 dataframe 으로 받게끔 했다.
        dict_ = {}

        for a_ship in start_a_ship:
            value = df[df.SHIP_CODE.values == a_ship]
            dict_[a_ship] = value

        print('Key : SHIP_CODE startswith A / Value : A Dataframe END.')
        
        return dict_
    '''
    SOG >2 Filtering
    '''
    def upper_2_dataframe(self, df):
        # Dict.values 안에 있는 dataframe -> list
        dict_to_lst = []

        for df in df.values():
            dict_to_lst.append(df[df.dSOG.values >= 2])

        # SOG <2 제외 하고 데이터 프레임 갱신
        not_empty_df = [full for full in dict_to_lst if not full.empty]

        print('SOG Filtering END.')

        return not_empty_df

    '''
    ADD Distance with haversine (Before coordinats -> After coordinates)
    '''
    # 거리 파생변수 추가해주는 dataframe
    def add_distance_df(self, df):

        for i in range(len(df)):
            dLat = df[i].dLat.tolist()
            dLon = df[i].dLon.tolist()
            position = []  # haversine 을 사용하기 위한 위, 경도 결합 리스트
            dist = []  # haversine 을 사용하여 직선거리를 담아 둘 리스트 (파생변수 담아 둘 리스트)

            for pos in zip(dLat, dLon):
                position.append(pos)

            for j in range(1, len(position)):
                dist.append(haversine(position[j - 1], position[j]) * 1000)  # haversine 은 default 가 km 이다.

            df[i]['dist'] = np.mean(dist)
            df[i]['dist'][1:] = dist

            position.clear()
            dist.clear()

        print('Derived variable dist END. ')
        return df


    '''
    Filtering Distance > 10
    '''
    def dist_upper_10_df(self, df):
        for i in range(len(df)):
            df[i] = df[i][df[i].dist.values > 10]

        print('Dist > 10 Filtering END.')
        return df

    '''
    Time_Series readability
    '''
    def reset_index_time_series(self, df):
        for i in range(len(df)):
            time_int = df[i].szMsgSendDT.values.tolist()
            time_str = []
            timestamp_ = []

            for j in range(len(time_int)):
                time_str.append(str(time_int[j]))
            # 시간 정보를 보기 좋게 바꿔준다
            for str_ in time_str:
                n = datetime.datetime.strptime(str_, "%Y%m%d%H%M%S%f")
                timestamp_.append(n.strftime("%Y-%m-%d-%H-%M-%S"))
            df[i]['szMsgSendDT'] = timestamp_

            time_str.clear()
            timestamp_.clear()

        print('Time_Series readability END.')

        return df

    '''
    ADD COG Distance 
    '''
    def add_cog_interval(self, df):
        for i in range(len(df)):
            df[i]['dCOG_diff'] = abs(df[i]['dCOG'].diff())

        print('Derived variable dCOG END.')
        return df


    '''
    ADD Time Interval 
    Moving Pandas 항적 분산을 위함
    '''
    def add_time_interval(self, df):
        
        for i in range(len(df)):
            df[i]['szMsgSendDT'] = pd.to_datetime(df[i]['szMsgSendDT'], format='%Y-%m-%d-%H-%M-%S')
            df[i]['time_interval'] = df[i]['szMsgSendDT'] - df[i]['szMsgSendDT'].shift(1)
            df[i]['time_interval'] = df[i]['time_interval'].fillna(pd.Timedelta(seconds=0))
        
        return df
    '''
    Save 3 Straight Line
    '''
    # 직선에 가장 가까운 상위 3가지 동선만 남기기
    def similar_straight_cog(self, df):

        flag = True

        for i in range(len(df)):
            df[i] = df[i].reset_index()
            df[i].drop(labels='index', axis=1, inplace=True)

            # 이전 좌표와 COG 간격 차이가 20이상이 되는 순간들의 index 좌표들만 추출
            index_lst = []
            for idx, col in df[i].iterrows():
                if col['dCOG_diff'] >= 20:
                    index_lst.append(idx)

            # 직선에 가까운 상위 3가지 동선 (인덱스 차이) 추출
            interval_lst = []
            for j in range(1, len(index_lst)):
                interval_lst.append(index_lst[j] - index_lst[j - 1])
            sorted_interval_lst = sorted(interval_lst, reverse=True)
            sort_3 = sorted_interval_lst[:3]

            final = []
            for k in range(1, len(index_lst)):
                if index_lst[k] - index_lst[k - 1] in sort_3:
                    final.append([index_lst[k - 1], index_lst[k]])

            indexes_to_keep = []
            for start, end in final:
                indexes_to_keep.extend(list(range(start, end + 1)))

            # 두번째 데이터 프레임 부터는 리스트를 초기화 하지 않는다.
            if flag:
                filtered_df = []

            # 인덱스에 해당 행만 남기고 나머지 행 제거
            filtered_df.append(df[i].iloc[indexes_to_keep])
            flag = False
        print('3 straight Line END.')
        return filtered_df

    '''
    Preprocessed Dictionary -> DataFrame
    딕셔너리 말고 데이터 프레임을 원하는 경우
    '''
    def dataframe_preprocessed(self, processed_dict):
        final_preprocessing = pd.DataFrame()

        for each_A_ship_df in processed_dict:
            final_preprocessing = pd.concat([final_preprocessing, each_A_ship_df])
        
        final_preprocessing.reset_index(drop = True, inplace = True)
        
        print('Preprocessed Dict -> DataFrame END.')
        return final_preprocessing

