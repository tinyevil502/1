using UnityEngine;
using System;

public class Health : MonoBehaviour
{
    [Header("血量设置")]
    [SerializeField] private float maxHealth = 100f;
    [SerializeField] private float currentHealth;
    
    [Header("事件")]
    public Action<float> OnHealthChanged;
    public Action<float> OnDamageTaken;
    public Action OnDeath;
    
    [Header("调试信息")]
    [SerializeField] private bool showDebugInfo = true;
    
    public float MaxHealth => maxHealth;
    public float CurrentHealth => currentHealth;
    public float HealthPercentage => currentHealth / maxHealth;
    public bool IsAlive => currentHealth > 0;
    
    private void Awake()
    {
        currentHealth = maxHealth;
    }
    
    private void Start()
    {
        OnHealthChanged?.Invoke(currentHealth);
    }
    
    public void TakeDamage(float damage)
    {
        if (!IsAlive) return;
        
        damage = Mathf.Max(0, damage);
        currentHealth = Mathf.Max(0, currentHealth - damage);
        
        if (showDebugInfo)
        {
            Debug.Log($"{gameObject.name} 受到 {damage} 点伤害，当前血量: {currentHealth}/{maxHealth}");
        }
        
        OnDamageTaken?.Invoke(damage);
        OnHealthChanged?.Invoke(currentHealth);
        
        if (currentHealth <= 0)
        {
            Die();
        }
    }
    
    public void Heal(float amount)
    {
        if (!IsAlive) return;
        
        amount = Mathf.Max(0, amount);
        currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
        
        if (showDebugInfo)
        {
            Debug.Log($"{gameObject.name} 恢复 {amount} 点血量，当前血量: {currentHealth}/{maxHealth}");
        }
        
        OnHealthChanged?.Invoke(currentHealth);
    }
    
    public void SetHealth(float health)
    {
        currentHealth = Mathf.Clamp(health, 0, maxHealth);
        OnHealthChanged?.Invoke(currentHealth);
        
        if (currentHealth <= 0 && IsAlive)
        {
            Die();
        }
    }
    
    public void SetMaxHealth(float newMaxHealth)
    {
        maxHealth = Mathf.Max(1, newMaxHealth);
        currentHealth = Mathf.Min(currentHealth, maxHealth);
        OnHealthChanged?.Invoke(currentHealth);
    }
    
    private void Die()
    {
        if (showDebugInfo)
        {
            Debug.Log($"{gameObject.name} 死亡了！");
        }
        
        OnDeath?.Invoke();
        
        // 移除所有buff效果
        var buffManager = GetComponent<BuffManager>();
        if (buffManager != null)
        {
            var activeBuffs = buffManager.GetActiveBuffs();
            foreach (var buff in activeBuffs)
            {
                buffManager.RemoveBuff(buff.buffId);
            }
        }
        
        // 可以在这里添加死亡效果
        HandleDeath();
    }
    
    private void HandleDeath()
    {
        // 这里可以添加死亡处理逻辑
        // 例如播放死亡动画、掉落物品、销毁对象等
        
        // 简单示例：延迟销毁对象
        Destroy(gameObject, 1f);
    }
    
    // 用于调试的方法
    [ContextMenu("测试伤害10点")]
    public void TestDamage()
    {
        TakeDamage(10f);
    }
    
    [ContextMenu("恢复满血")]
    public void TestHeal()
    {
        SetHealth(maxHealth);
    }
}