/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "vSPI.h"		//引入自定义头文件
#include "MCP4921.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
#define DAC_CMD_ACTIVE     0x30u
#define DAC_LOW_CODE       0x000u
#define DAC_FULL_CODE      0x0fffu
#define AMP_MIN_V          5u
#define AMP_MAX_V          20u
#define AMP_STEP_V         5u
#define FREQ_MULT_MIN      1u
#define FREQ_MULT_MAX      8u
#define KEY_DEBOUNCE_MS    180u
#define WAVE_PHASE_LIMIT   40u

static uint8_t g_freq_mult = 1u;
static uint8_t g_amp_set_v = 20u;
static uint8_t g_external_mode = 0u;
static uint8_t g_output_enabled = 1u;
static uint8_t g_wave_high = 0u;
static uint32_t g_last_wave_tick = 0u;
static uint32_t g_last_key_tick = 0u;
static uint32_t g_wave_phase = 0u;
static GPIO_PinState g_last_ext_trig = GPIO_PIN_RESET;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
static uint16_t App_AmplitudeToDacCode(uint8_t amplitude_v);
static uint8_t App_IsKeyPressed(GPIO_TypeDef *port, uint16_t pin);
static void App_ResetWaveTiming(uint32_t now);
static void App_WriteWaveLow(void);
static void App_WriteWaveHigh(void);
static void App_ProcessKeys(void);
static void App_ProcessExternalTrigger(void);
static void App_ProcessWaveform(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
static uint16_t App_AmplitudeToDacCode(uint8_t amplitude_v)
{
  if (amplitude_v < AMP_MIN_V)
  {
    amplitude_v = AMP_MIN_V;
  }
  if (amplitude_v > AMP_MAX_V)
  {
    amplitude_v = AMP_MAX_V;
  }

  return (uint16_t)(((uint32_t)amplitude_v * DAC_FULL_CODE) / AMP_MAX_V);
}

static uint8_t App_IsKeyPressed(GPIO_TypeDef *port, uint16_t pin)
{
  return (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_RESET) ? 1u : 0u;
}

static void App_ResetWaveTiming(uint32_t now)
{
  g_last_wave_tick = now;
  g_wave_phase = 0u;
}

static void App_WriteWaveLow(void)
{
  MCP4921Write(DAC_CMD_ACTIVE, DAC_LOW_CODE);
  HAL_GPIO_WritePin(WAVE_MARK_GPIO_Port, WAVE_MARK_Pin, GPIO_PIN_RESET);
  g_wave_high = 0u;
}

static void App_WriteWaveHigh(void)
{
  MCP4921Write(DAC_CMD_ACTIVE, App_AmplitudeToDacCode(g_amp_set_v));
  HAL_GPIO_WritePin(WAVE_MARK_GPIO_Port, WAVE_MARK_Pin, GPIO_PIN_SET);
  g_wave_high = 1u;
}

static void App_ProcessKeys(void)
{
  uint32_t now = HAL_GetTick();

  if ((now - g_last_key_tick) < KEY_DEBOUNCE_MS)
  {
    return;
  }

  if (App_IsKeyPressed(KEY_FREQ_GPIO_Port, KEY_FREQ_Pin) != 0u)
  {
    g_freq_mult++;
    if (g_freq_mult > FREQ_MULT_MAX)
    {
      g_freq_mult = FREQ_MULT_MIN;
    }
    App_ResetWaveTiming(now);
    g_last_key_tick = now;
  }
  else if (App_IsKeyPressed(KEY_AMP_UP_GPIO_Port, KEY_AMP_UP_Pin) != 0u)
  {
    if (g_amp_set_v < AMP_MAX_V)
    {
      g_amp_set_v += AMP_STEP_V;
      if (g_wave_high != 0u)
      {
        App_WriteWaveHigh();
      }
    }
    g_last_key_tick = now;
  }
  else if (App_IsKeyPressed(KEY_AMP_DOWN_GPIO_Port, KEY_AMP_DOWN_Pin) != 0u)
  {
    if (g_amp_set_v > AMP_MIN_V)
    {
      g_amp_set_v -= AMP_STEP_V;
      if (g_wave_high != 0u)
      {
        App_WriteWaveHigh();
      }
    }
    g_last_key_tick = now;
  }
  else if (App_IsKeyPressed(KEY_MODE_GPIO_Port, KEY_MODE_Pin) != 0u)
  {
    g_external_mode ^= 1u;
    g_output_enabled = (g_external_mode == 0u) ? 1u : 0u;
    App_ResetWaveTiming(now);
    App_WriteWaveLow();
    g_last_key_tick = now;
  }
}

static void App_ProcessExternalTrigger(void)
{
  GPIO_PinState now_state = HAL_GPIO_ReadPin(EXT_TRIG_GPIO_Port, EXT_TRIG_Pin);

  if (g_external_mode != 0u)
  {
    if ((g_last_ext_trig == GPIO_PIN_RESET) && (now_state == GPIO_PIN_SET))
    {
      g_output_enabled = 1u;
      App_ResetWaveTiming(HAL_GetTick());
      App_WriteWaveHigh();
    }
  }

  g_last_ext_trig = now_state;
}

static void App_ProcessWaveform(void)
{
  uint32_t now = HAL_GetTick();
  uint32_t elapsed_ms = now - g_last_wave_tick;

  if (g_output_enabled == 0u)
  {
    App_WriteWaveLow();
    App_ResetWaveTiming(now);
    return;
  }

  if (elapsed_ms == 0u)
  {
    return;
  }

  g_last_wave_tick = now;
  g_wave_phase += elapsed_ms * g_freq_mult;

  while (g_wave_phase >= WAVE_PHASE_LIMIT)
  {
    g_wave_phase -= WAVE_PHASE_LIMIT;
    if (g_wave_high != 0u)
    {
      App_WriteWaveLow();
    }
    else
    {
      App_WriteWaveHigh();
    }
  }
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  /* USER CODE BEGIN 2 */
  App_WriteWaveLow();
  App_ResetWaveTiming(HAL_GetTick());
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    App_ProcessKeys();
    App_ProcessExternalTrigger();
    App_ProcessWaveform();
    HAL_Delay(1);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
