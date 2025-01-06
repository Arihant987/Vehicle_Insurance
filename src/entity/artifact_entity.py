from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    trained_file_path:str
    test_file_path:str

@dataclass
class DataValidationArtifact:
    validation_status:bool
    message:str
    validation_report_file_path:str

@dataclass
class DataTransformationArtifact:
    transformed_object_file_path:str
    transformed_train_file_path:str
    transformed_test_file_path:str
    
@dataclass
class ClassifactionMetricArtifact:
    f1_score:float
    precision_score:float
    recall_score:float
    classification_report:str

@dataclass
class ModelTrainerArtifact:
    trained_model_file_path:str
    metric_artifact:ClassifactionMetricArtifact

@dataclass
class ModelEvaluationArtifact:
    is_model_aacepted:bool
    changed_accuracy:float
    s3_model_path:str # model.pkl only
    trained_model_path:str
