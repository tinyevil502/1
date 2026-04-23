using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public abstract class Buff
{
    public string buffId;
    public string buffName;
    public float duration;
    public float remainingTime;
    public bool isActive;
    
    protected GameObject target;
    protected MonoBehaviour context;
    
    public Buff(string id, string name, float duration)
    {
        this.buffId = id;
        this.buffName = name;
        this.duration = duration;
        this.remainingTime = duration;
        this.isActive = false;
    }
    
    public virtual void Initialize(GameObject target, MonoBehaviour context)
    {
        this.target = target;
        this.context = context;
        this.isActive = true;
        OnApply();
    }
    
    public virtual void Update(float deltaTime)
    {
        if (!isActive) return;
        
        remainingTime -= deltaTime;
        OnUpdate(deltaTime);
        
        if (remainingTime <= 0)
        {
            OnExpire();
            isActive = false;
        }
    }
    
    public virtual void Remove()
    {
        OnRemove();
        isActive = false;
    }
    
    protected abstract void OnApply();
    protected abstract void OnUpdate(float deltaTime);
    protected abstract void OnExpire();
    protected abstract void OnRemove();
}

public class BuffManager : MonoBehaviour
{
    private List<Buff> activeBuffs = new List<Buff>();
    
    private void Update()
    {
        // 更新所有活跃的buff
        for (int i = activeBuffs.Count - 1; i >= 0; i--)
        {
            activeBuffs[i].Update(Time.deltaTime);
            
            // 移除已过期的buff
            if (!activeBuffs[i].isActive)
            {
                activeBuffs.RemoveAt(i);
            }
        }
    }
    
    public void AddBuff(Buff buff)
    {
        // 检查是否已存在相同类型的buff
        var existingBuff = activeBuffs.Find(b => b.buffId == buff.buffId);
        if (existingBuff != null)
        {
            // 刷新持续时间
            existingBuff.remainingTime = buff.duration;
            return;
        }
        
        buff.Initialize(gameObject, this);
        activeBuffs.Add(buff);
    }
    
    public void RemoveBuff(string buffId)
    {
        var buff = activeBuffs.Find(b => b.buffId == buffId);
        if (buff != null)
        {
            buff.Remove();
            activeBuffs.Remove(buff);
        }
    }
    
    public bool HasBuff(string buffId)
    {
        return activeBuffs.Exists(b => b.buffId == buffId && b.isActive);
    }
    
    public List<Buff> GetActiveBuffs()
    {
        return new List<Buff>(activeBuffs);
    }
}