{
    "train_micro_batch_size_per_gpu": "auto",
    "zero_allow_untested_optimizer": true,
    "bf16": {
      "enabled": "auto"
    },  
    "zero_optimization": {
      "stage": 3,
      "offload_optimizer": {
          "device": "cpu",
          "pin_memory": true,
          "buffer_count": 4
      },
      "offload_param": {
          "device": "cpu",
          "pin_memory": true
      },
      "stage3_gather_16bit_weights_on_model_save": true
  },
  "steps_per_print": 100
}