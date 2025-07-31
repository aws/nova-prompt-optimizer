/**
 * Frontend performance tests
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { performanceMonitor, MemoryOptimizer, BundleAnalyzer } from '../../lib/performance'

// Mock performance API
const mockPerformance = {
  now: vi.fn(() => Date.now()),
  mark: vi.fn(),
  measure: vi.fn(),
  getEntriesByName: vi.fn(() => []),
  getEntriesByType: vi.fn(() => []),
  memory: {
    usedJSHeapSize: 10000000,
    totalJSHeapSize: 20000000,
    jsHeapSizeLimit: 100000000
  }
}

// Mock PerformanceObserver
class MockPerformanceObserver {
  callback: (list: any) => void
  
  constructor(callback: (list: any) => void) {
    this.callback = callback
  }
  
  observe() {}
  disconnect() {}
}

global.PerformanceObserver = MockPerformanceObserver as any
global.performance = mockPerformance as any

describe('Performance Monitoring', () => {
  beforeEach(() => {
    performanceMonitor.clearMetrics()
    vi.clearAllMocks()
  })

  afterEach(() => {
    performanceMonitor.clearMetrics()
  })

  describe('PerformanceMonitor', () => {
    it('should record metrics correctly', () => {
      const metric = {
        name: 'test-operation',
        duration: 150,
        timestamp: Date.now(),
        metadata: { component: 'TestComponent' }
      }

      performanceMonitor.recordMetric(metric)
      const metrics = performanceMonitor.getMetrics('test-operation')

      expect(metrics).toHaveLength(1)
      expect(metrics[0]).toEqual(metric)
    })

    it('should filter metrics by name', () => {
      performanceMonitor.recordMetric({
        name: 'operation-a',
        duration: 100,
        timestamp: Date.now()
      })
      
      performanceMonitor.recordMetric({
        name: 'operation-b',
        duration: 200,
        timestamp: Date.now()
      })

      const metricsA = performanceMonitor.getMetrics('operation-a')
      const metricsB = performanceMonitor.getMetrics('operation-b')

      expect(metricsA).toHaveLength(1)
      expect(metricsB).toHaveLength(1)
      expect(metricsA[0].name).toBe('operation-a')
      expect(metricsB[0].name).toBe('operation-b')
    })

    it('should calculate metrics summary correctly', () => {
      const durations = [100, 200, 300, 400, 500]
      
      durations.forEach((duration, index) => {
        performanceMonitor.recordMetric({
          name: 'test-operation',
          duration,
          timestamp: Date.now() + index
        })
      })

      const summary = performanceMonitor.getMetricsSummary('test-operation')

      expect(summary).toBeDefined()
      expect(summary!.count).toBe(5)
      expect(summary!.min).toBe(100)
      expect(summary!.max).toBe(500)
      expect(summary!.avg).toBe(300)
      expect(summary!.p95).toBe(500) // For small dataset, p95 is max
    })

    it('should limit stored metrics to max size', () => {
      const monitor = new (performanceMonitor.constructor as any)(5) // Max 5 metrics
      
      // Add 10 metrics
      for (let i = 0; i < 10; i++) {
        monitor.recordMetric({
          name: `operation-${i}`,
          duration: i * 100,
          timestamp: Date.now() + i
        })
      }

      const allMetrics = monitor.getMetrics()
      expect(allMetrics).toHaveLength(5)
      
      // Should keep the most recent 5
      expect(allMetrics[0].name).toBe('operation-5')
      expect(allMetrics[4].name).toBe('operation-9')
    })

    it('should get memory info when available', () => {
      const memoryInfo = performanceMonitor.getMemoryInfo()

      expect(memoryInfo).toBeDefined()
      expect(memoryInfo!.usedJSHeapSize).toBe(10000000)
      expect(memoryInfo!.totalJSHeapSize).toBe(20000000)
      expect(memoryInfo!.jsHeapSizeLimit).toBe(100000000)
    })

    it('should return null for memory info when not available', () => {
      const originalMemory = (global.performance as any).memory
      delete (global.performance as any).memory

      const memoryInfo = performanceMonitor.getMemoryInfo()
      expect(memoryInfo).toBeNull()

      // Restore
      ;(global.performance as any).memory = originalMemory
    })
  })

  describe('Performance Measurement Decorator', () => {
    it('should measure function execution time', async () => {
      const { measurePerformance } = await import('../../lib/performance')
      
      class TestClass {
        @measurePerformance('test-method')
        async testMethod() {
          await new Promise(resolve => setTimeout(resolve, 100))
          return 'result'
        }
      }

      const instance = new TestClass()
      const result = await instance.testMethod()

      expect(result).toBe('result')
      
      const metrics = performanceMonitor.getMetrics('test-method')
      expect(metrics).toHaveLength(1)
      expect(metrics[0].duration).toBeGreaterThan(90) // Allow some variance
    })

    it('should record error metrics when function throws', async () => {
      const { measurePerformance } = await import('../../lib/performance')
      
      class TestClass {
        @measurePerformance('error-method')
        async errorMethod() {
          throw new Error('Test error')
        }
      }

      const instance = new TestClass()
      
      await expect(instance.errorMethod()).rejects.toThrow('Test error')
      
      const metrics = performanceMonitor.getMetrics('error-method-error')
      expect(metrics).toHaveLength(1)
      expect(metrics[0].metadata?.error).toBe('Test error')
    })
  })

  describe('MemoryOptimizer', () => {
    it('should optimize image size', async () => {
      // Mock canvas and image
      const mockCanvas = {
        width: 0,
        height: 0,
        getContext: vi.fn(() => ({
          drawImage: vi.fn()
        })),
        toDataURL: vi.fn(() => 'data:image/jpeg;base64,optimized')
      }

      const mockImage = {
        width: 1600,
        height: 1200,
        onload: null as any,
        src: ''
      }

      global.document.createElement = vi.fn((tag) => {
        if (tag === 'canvas') return mockCanvas as any
        return {} as any
      })

      global.Image = vi.fn(() => mockImage) as any

      const optimizedSrc = MemoryOptimizer.optimizeImage('test.jpg', 800, 0.8)
      
      // Trigger onload
      mockImage.onload()
      
      const result = await optimizedSrc
      expect(result).toBe('data:image/jpeg;base64,optimized')
      expect(mockCanvas.width).toBe(640) // Scaled down proportionally
      expect(mockCanvas.height).toBe(480)
    })

    it('should cache images correctly', async () => {
      const mockImage = {
        onload: null as any,
        onerror: null as any,
        src: ''
      }

      global.Image = vi.fn(() => mockImage) as any

      const cachePromise = MemoryOptimizer.cacheImage('test.jpg')
      
      // Trigger onload
      setTimeout(() => mockImage.onload(), 0)
      
      const cachedImage = await cachePromise
      expect(cachedImage).toBe(mockImage)
      expect(MemoryOptimizer.getImageCacheSize()).toBe(1)
    })

    it('should limit cache size', async () => {
      const maxSize = 50 // Default max cache size
      
      // Fill cache beyond max size
      for (let i = 0; i < maxSize + 5; i++) {
        const mockImage = {
          onload: null as any,
          onerror: null as any,
          src: ''
        }
        
        global.Image = vi.fn(() => mockImage) as any
        
        const cachePromise = MemoryOptimizer.cacheImage(`test-${i}.jpg`)
        setTimeout(() => mockImage.onload(), 0)
        await cachePromise
      }

      expect(MemoryOptimizer.getImageCacheSize()).toBe(maxSize)
    })

    it('should clear image cache', () => {
      MemoryOptimizer.clearImageCache()
      expect(MemoryOptimizer.getImageCacheSize()).toBe(0)
    })
  })

  describe('BundleAnalyzer', () => {
    it('should analyze chunk sizes', async () => {
      // Mock DOM scripts
      const mockScripts = [
        { src: 'https://example.com/chunk-123.js' },
        { src: 'https://example.com/vendor-456.js' },
        { src: 'https://example.com/main.js' }
      ]

      global.document.querySelectorAll = vi.fn(() => mockScripts as any)
      
      // Mock fetch responses
      global.fetch = vi.fn((url) => {
        const size = url.includes('chunk') ? 50000 : 
                    url.includes('vendor') ? 200000 : 0
        
        return Promise.resolve({
          headers: {
            get: (header: string) => header === 'content-length' ? size.toString() : null
          }
        } as any)
      })

      const chunks = await BundleAnalyzer.analyzeChunkSizes()
      
      expect(chunks['https://example.com/chunk-123.js']).toBe(50000)
      expect(chunks['https://example.com/vendor-456.js']).toBe(200000)
    })

    it('should calculate total bundle size', async () => {
      const mockScripts = [
        { src: 'https://example.com/chunk-123.js' },
        { src: 'https://example.com/vendor-456.js' }
      ]

      global.document.querySelectorAll = vi.fn(() => mockScripts as any)
      
      global.fetch = vi.fn(() => Promise.resolve({
        headers: {
          get: () => '100000'
        }
      } as any))

      const totalSize = await BundleAnalyzer.getTotalBundleSize()
      expect(totalSize).toBe(200000) // 2 chunks × 100KB each
    })
  })

  describe('Performance Thresholds', () => {
    it('should warn about slow operations', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      performanceMonitor.recordMetric({
        name: 'slow-operation',
        duration: 2000, // 2 seconds - above 1s threshold
        timestamp: Date.now()
      })

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Slow operation detected: slow-operation took 2000.00ms')
      )

      consoleSpy.mockRestore()
    })

    it('should not warn about fast operations', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      performanceMonitor.recordMetric({
        name: 'fast-operation',
        duration: 500, // 0.5 seconds - below 1s threshold
        timestamp: Date.now()
      })

      expect(consoleSpy).not.toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Network Timing', () => {
    it('should measure network timing', async () => {
      const mockEntry = {
        domainLookupStart: 100,
        domainLookupEnd: 120,
        connectStart: 120,
        connectEnd: 150,
        requestStart: 150,
        responseStart: 200,
        responseEnd: 250
      }

      mockPerformance.getEntriesByName.mockReturnValue([mockEntry])
      
      global.fetch = vi.fn(() => Promise.resolve({} as any))

      const timing = await performanceMonitor.measureNetworkTiming('https://api.example.com/test')

      expect(timing.dns).toBe(20) // 120 - 100
      expect(timing.tcp).toBe(30) // 150 - 120
      expect(timing.request).toBe(50) // 200 - 150
      expect(timing.response).toBe(50) // 250 - 200
      expect(timing.total).toBeGreaterThan(0)
    })

    it('should handle network timing errors gracefully', async () => {
      global.fetch = vi.fn(() => Promise.reject(new Error('Network error')))

      const timing = await performanceMonitor.measureNetworkTiming('https://api.example.com/test')

      expect(timing.dns).toBe(0)
      expect(timing.tcp).toBe(0)
      expect(timing.request).toBe(0)
      expect(timing.response).toBe(0)
      expect(timing.total).toBeGreaterThan(0)
    })
  })
})