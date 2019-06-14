from abc import abstractmethod, ABC

counter =0
class BaseCloudInterfce(ABC):
    """ Base class to define instance plugin interface. """

    def __init__(self):
        """ constructor method for instance"""
        pass

    @abstractmethod
    def connect_to_peer(self):
        """ establish connection with peer """
        pass

    @abstractmethod
    def getRegion(self):
        """ returns instance list """
        pass

    @abstractmethod
    def addRegion(self):
        """ returns instance list """
        pass

    @abstractmethod
    def deleteRegion(self):
        """ returns instance list """
        pass
    
    @abstractmethod
    def updateRegion(self):
        """ returns instance list """
        pass
    
    @abstractmethod
    def getVpc(self):
        """ returns instance list """
        pass

    @abstractmethod
    def addVpc(self):
        """ returns instance list """
        pass
    
    @abstractmethod
    def deleteVpc(self):
        """ returns instance list """
        pass

    @abstractmethod
    def updateVpc(self):
        """ returns instance list """
        pass

    @abstractmethod
    def getSecurityGroup(self):
        """ returns instance list """
        pass

    @abstractmethod
    def addSecurityGroup(self):
        """ returns instance list """
        pass

    @abstractmethod
    def deleteSecurityGroup(self):
        """ returns instance list """
        pass

    @abstractmethod
    def updateSecurityGroup(self):
        """ returns instance list """
        pass

    @abstractmethod
    def getIngressRule(self):
        """ returns instance list """
        pass

    @abstractmethod
    def addIngressRule(self):
        """ returns instance list """
        pass

    @abstractmethod
    def deleteIngressRule(self):
        """ returns instance list """
        pass

    @abstractmethod
    def updateIngressRule(self):
        """ returns instance list """
        pass

    @abstractmethod
    def getEgressRule(self):
        """ returns instance list """
        pass

    @abstractmethod
    def addEgressRule(self):
        """ returns instance list """
        pass

    @abstractmethod
    def deleteEgressRule(self):
        """ returns instance list """
        pass

    @abstractmethod
    def updateEgressRule(self):
        """ returns instance list """
        pass


class CloudFactory:
    global counter
    running_cloud = {}
    index = 0
    def __init__(cls,obj):
        global counter
        cls.index = counter
        tmp_cloud = {}
        tmp_cloud[counter] = obj
        cls.running_cloud.update(tmp_cloud)
        counter = counter + 1
        #return cls.running_cloud[counter-1]

    @classmethod
    def getInstance(cls,id):
        return cls.running_cloud[id]






