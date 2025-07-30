using UnityEngine;
using System.Collections;

public class PoisonBuff : Buff
{
    private float damageAmount;
    private float damageInterval;
    private float timeSinceLastDamage;
    private Health targetHealth;
    
    public PoisonBuff(float damage = 1f, float interval = 0.2f, float duration = 5f) 
        : base("poison", "中毒", duration)
    {
        this.damageAmount = damage;
        this.damageInterval = interval;
        this.timeSinceLastDamage = 0f;
    }
    
    protected override void OnApply()
    {
        // 获取目标的血量组件
        targetHealth = target.GetComponent<Health>();
        if (targetHealth == null)
        {
            Debug.LogWarning($"目标 {target.name} 没有Health组件，无法应用中毒效果");
            isActive = false;
            return;
        }
        
        Debug.Log($"{target.name} 中毒了！将在 {duration} 秒内每 {damageInterval} 秒受到 {damageAmount} 点伤害");
        
        // 可以在这里添加视觉效果
        ShowPoisonEffect(true);
    }
    
    protected override void OnUpdate(float deltaTime)
    {
        if (targetHealth == null) return;
        
        timeSinceLastDamage += deltaTime;
        
        // 检查是否到了造成伤害的时间
        if (timeSinceLastDamage >= damageInterval)
        {
            // 造成伤害
            targetHealth.TakeDamage(damageAmount);
            Debug.Log($"{target.name} 受到中毒伤害: {damageAmount}，剩余血量: {targetHealth.CurrentHealth}");
            
            // 重置计时器
            timeSinceLastDamage = 0f;
            
            // 可以在这里添加伤害特效
            ShowDamageEffect();
        }
    }
    
    protected override void OnExpire()
    {
        Debug.Log($"{target.name} 的中毒效果结束了");
        ShowPoisonEffect(false);
    }
    
    protected override void OnRemove()
    {
        Debug.Log($"{target.name} 的中毒效果被移除了");
        ShowPoisonEffect(false);
    }
    
    private void ShowPoisonEffect(bool show)
    {
        // 这里可以控制中毒的视觉效果
        // 例如改变敌人颜色、添加粒子效果等
        var renderer = target.GetComponent<Renderer>();
        if (renderer != null)
        {
            if (show)
            {
                // 添加绿色调表示中毒
                renderer.material.color = Color.green;
            }
            else
            {
                // 恢复原色
                renderer.material.color = Color.white;
            }
        }
    }
    
    private void ShowDamageEffect()
    {
        // 这里可以添加每次伤害的特效
        // 例如数字飘字、粒子爆发等
        
        // 简单的闪烁效果示例
        var renderer = target.GetComponent<Renderer>();
        if (renderer != null && context != null)
        {
            context.StartCoroutine(DamageFlash(renderer));
        }
    }
    
    private IEnumerator DamageFlash(Renderer renderer)
    {
        Color originalColor = renderer.material.color;
        renderer.material.color = Color.red;
        yield return new WaitForSeconds(0.1f);
        renderer.material.color = originalColor;
    }
}