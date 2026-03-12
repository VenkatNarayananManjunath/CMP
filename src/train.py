import os
import mlflow
import numpy as np
import torch
import torch.nn as nn
from datasets import load_dataset
from transformers import ViTForImageClassification, ViTImageProcessor, TrainingArguments, Trainer
import evaluate

def train_model():
    # Set up MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("ViT_CIFAR10_Classification")

    with mlflow.start_run() as run:
        print("Starting training run...")
        # Load dataset
        dataset = load_dataset("cifar10")
        
        # Take a small subset to run faster during tests/automation
        train_ds = dataset['train'].shuffle(seed=42).select(range(1000))
        test_ds = dataset['test'].shuffle(seed=42).select(range(200))

        # Model from huggingface
        model_name = "google/vit-base-patch16-224-in21k"
        processor = ViTImageProcessor.from_pretrained(model_name)
        
        id2label = {id: label for id, label in enumerate(train_ds.features['label'].names)}
        label2id = {label: id for id, label in id2label.items()}

        model = ViTForImageClassification.from_pretrained(
            model_name,
            num_labels=10,
            id2label=id2label,
            label2id=label2id,
            ignore_mismatched_sizes=True
        )

        def process_example(example_batch):
            inputs = processor([x.convert("RGB") for x in example_batch['img']], return_tensors='pt')
            inputs['labels'] = example_batch['label']
            return inputs

        train_ds = train_ds.with_transform(process_example)
        test_ds = test_ds.with_transform(process_example)

        metric = evaluate.load("accuracy")

        def compute_metrics(p):
            predictions = np.argmax(p.predictions, axis=1)
            return metric.compute(predictions=predictions, references=p.label_ids)

        training_args = TrainingArguments(
            output_dir="./vit-cifar10",
            per_device_train_batch_size=16,
            eval_strategy="epoch",  # updated param
            num_train_epochs=1,     # keep 1 for demo
            fp16=torch.cuda.is_available(),
            save_strategy="epoch",
            logging_steps=50,
            learning_rate=2e-5,
            save_total_limit=1,
            remove_unused_columns=False,
            push_to_hub=False,
            report_to="none" # We will use MLflow callback manually
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_ds,
            eval_dataset=test_ds,
            compute_metrics=compute_metrics,
        )

        # Log parameters
        mlflow.log_params(training_args.to_dict())

        # Train
        train_results = trainer.train()
        
        # Log metrics
        mlflow.log_metrics({
            "train_loss": train_results.metrics["train_loss"],
            "train_runtime": train_results.metrics["train_runtime"]
        })

        # Evaluate
        eval_results = trainer.evaluate()
        mlflow.log_metrics({
            "eval_loss": eval_results["eval_loss"],
            "eval_accuracy": eval_results["eval_accuracy"]
        })

        # Save model locally and to MLflow
        trainer.save_model("./vit-cifar10-final")
        mlflow.pytorch.log_model(model, "vit_model")

        print("Training completed. Model saved and metrics logged to MLflow.")

if __name__ == "__main__":
    train_model()
