def apply_horizon_crossings(self, prn_df):
        """
        Apply the horizon crossings to the prn_df
        1. create a list of horizon crossing epochs
        2. loop through the list, first iteration always out of site
           alternate between out of sight and missing
        3. Set the nature of the epochs to missing or out of sight
        """
        prn_df = prn_df.copy()
        prn = prn_df['num'].dropna().iloc[0]
        sys = prn_df['sys'].dropna().iloc[0]
        prn_df.set_index('epoch', inplace=True)
        nanosecond = pd.Timedelta('1ns') # used to prevent arc windows overlapping
        
        start_of_day = prn_df.index.min().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = prn_df.index.max().replace(hour=23, minute=59, second=30, microsecond=0)
        
        horizon_crossing_list = [start_of_day]
        
        prn_horizon_crossing = self.horizon_crossing_df.query('sys == @sys & prn == @prn')
        if not prn_horizon_crossing.empty:
            for idx, row in prn_horizon_crossing.iterrows():
                horizon_crossing_list.append(row['entering_epoch'])
                horizon_crossing_list.append(row['leaving_epoch'])
            
        horizon_crossing_list.append(end_of_day)
        
        out_of_sight_flag = True
            
        for idx, crossing_epoch in enumerate(horizon_crossing_list[:-1]): # miss last element as its added anyway
            
            entering_epoch = crossing_epoch 
            exiting_epoch = horizon_crossing_list[idx + 1]
            
            if entering_epoch == exiting_epoch:
                out_of_sight_flag = not out_of_sight_flag
                continue
            
            entering_epoch += nanosecond
            
            if out_of_sight_flag: # out of sight epochs
                
                out_of_sight_epochs = (prn_df.index >= entering_epoch) & (prn_df.index <= exiting_epoch)
                is_na_mask = prn_df['el'].isna()
                combined_mask = out_of_sight_epochs & is_na_mask
                # set as out of sight
                prn_df.loc[combined_mask, 'nature'] = 'out of sight'
                out_of_sight_flag = False
            
            else: # in sight epochs

                in_sight_epochs_mask = (prn_df.index >= entering_epoch) & (prn_df.index <= exiting_epoch)
                
                is_na_mask = prn_df['el'].isna()
                # Create a mask where nature is 'out of sight'
                flagged_out_of_sight_mask = (prn_df['nature'] == 'out of sight')
                
                # Combine masks to find 'in sight' epochs that are currently marked 'out of sight'
                combined_mask = in_sight_epochs_mask & flagged_out_of_sight_mask & is_na_mask
                
                # Update 'nature' for the relevant rows
                prn_df.loc[combined_mask, 'nature'] = 'missing'        
                
                out_of_sight_flag = True
            
        return prn_df