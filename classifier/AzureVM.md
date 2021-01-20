# Azure Ubuntu VM for Classification

This step-by-step instruction covers prepping Azure Ubuntu VM for the school homepage classification.

### Creating Azure VM with Ubuntu image

------

**1. From Azure portal, click "Virtual machines" from Azure services**

   ![Azure VM icon](images/01_azure_vm_icon.png) 				 ![Azure VM sidebar](images/01_azure_vm_sidebar.png)

**2. Click "Add" and select "Virtual machine"**

![Add VM](images/02_azure_add_vm.png) 

**3. Complete the form using following instruction**

   - Subscription
     - For ADS, it should be "ADS Unstructured Storage"
   - Resource group
     - Select your resource group if you have already created one from any previous activities OR create one
     - If you are to create one please follow this convention
       - [dept]-[your netID]-[testing/prod]-rg
       - (e.g.,) ads-jhp-testing-rg
   - Virtual machine name
     - You may name anything but suggest something that reflects your project
       - (e.g.,) SchoolTextVM
   - Region
     - East US (default) is fine unless you have other requirements
   - Availability
     - Default is fine (No infrastructure redundancy required)
   - Image
     - Ubuntu Server 18.04 LTS - Gen 1 (current at the time of writing 01/19/2021)
   - Size
     - Default is fine (Standard_D2s_v3 - 2 vcpus, 8 GiB memory - $70.08/month - 01/19/2021)
   - Authentication type
     - Password
   - Username
     - Something that is easy to remember and you can share with others but not extremely easy
       - (e.g.,) schooltext
   - Password
     - Something that is easy to remember and you can share with others but not extremely easy
       - (e.g.,) SchoolText2021
   - Public inbound ports
     - Allow selected ports
   - Select inbound ports
     - SSH (22)
   - CLICK "Review + create"

![Azure Create VM](images/03_azure_create_vm.png)  

**4. Check "Validation passed" banner and click "Create"** 

   - Once completed then click "Go to resource"

![Azure VM Deployed](images/04_azure_vm_deployed.png)  



**5. Click "Networking" (just under the "Settings") from the side bar and then click "Add inbound port rule"**

![Azure VM Networking](images/05_azure_vm_networking.png)  

**6. Need to open port 3389 in order to support "Remote Desktop Protocol" (RDP) access. Follow instruction below to add a new inbound security rule to open port 3389, then click "Add"**

   - Source: Any
   - Source port ranges: *
   - Destination: Any
   - Destination port ranges: 3389
   - Protocol: TCP
   - Action: Allow
   - Priority: default is fine (310)
   - Name: Port_3389

![Azure VM open port 3389](images/06_azure_port.png)  

