def Federated_Unlearning():
    """Step 1.Set the parameters for Federated Unlearning"""
    FL_params = Arguments()
    torch.manual_seed(FL_params.seed)
    #kwargs for data loader 
    print(60*'=')
    print("Step1. Federated Learning Settings \n We use dataset: "+FL_params.data_name+(" for our Federated Unlearning experiment.\n"))


    """Step 2. construct the necessary user private data set required for federated learning, as well as a common test set"""
    print(60*'=')
    print("Step2. Client data loaded, testing data loaded!!!\n       Initial Model loaded!!!")
    #加载数据   
    init_global_model = model_init(FL_params.data_name)
    client_all_loaders, test_loader = data_init(FL_params)

    selected_clients=np.random.choice(range(FL_params.N_total_client),size=FL_params.N_client, replace=False)
    client_loaders = list()
    for idx in selected_clients:
        client_loaders.append(client_all_loaders[idx])
    # client_all_loaders = client_loaders[selected_clients]
    # client_loaders, test_loader, shadow_client_loaders, shadow_test_loader = data_init_with_shadow(FL_params)
    """
    This section of the code gets the initialization model init Global Model
    User data loader for FL training Client_loaders and test data loader Test_loader
    User data loader for covert FL training, Shadow_client_loaders, and test data loader Shadowl_test_loader
    """

    """Step 3. Select a client's data to forget，1.Federated Learning, 2.Unlearning(FedEraser), and 3.(Accumulating)Unlearing without calibration"""
    print(60*'=')
    print("Step3. Fedearated Learning and Unlearning Training...")
    # 
    old_GMs, unlearn_GMs, uncali_unlearn_GMs = federated_learning_unlearning(init_global_model, 
                                                                                            client_loaders, 
                                                                                            test_loader, 
                                                                                            FL_params)

    if(FL_params.if_retrain == True):
        
        t1 = time.time()
        retrain_GMs = FL_Retrain(init_global_model, client_loaders, test_loader, FL_params)
        t2 = time.time()
        print("Time using = {} seconds".format(t2-t1))

    """Step 4  The member inference attack model is built based on the output of the Target Global Model on client_loaders and test_loaders.In this case, we only do the MIA attack on the model at the end of the training"""
    
    """MIA:Based on the output of oldGM model, MIA attack model was built, and then the attack model was used to attack unlearn GM. If the attack accuracy significantly decreased, it indicated that our unlearn method was indeed effective to remove the user's information"""
    print(60*'=')
    print("Step4. Membership Inference Attack aganist GM...")

    T_epoch = -1
    # MIA setting:Target model == Shadow Model
    old_GM = old_GMs[T_epoch]
    attack_model = train_attack_model(old_GM, client_loaders, test_loader, FL_params)


    print("\nEpoch  = {}".format(T_epoch))
    print("Attacking against FL Standard  ")
    target_model = old_GMs[T_epoch]
    (ACC_old, PRE_old) = attack(target_model, attack_model, client_loaders, test_loader, FL_params)

    if(FL_params.if_retrain == True):
        print("Attacking against FL Retrain  ")
        target_model = retrain_GMs[T_epoch]
        (ACC_retrain, PRE_retrain) = attack(target_model, attack_model, client_loaders, test_loader, FL_params)

    print("Attacking against FL Unlearn  ")
    target_model = unlearn_GMs[T_epoch]
    (ACC_unlearn, PRE_unlearn) = attack(target_model, attack_model, client_loaders, test_loader, FL_params)
