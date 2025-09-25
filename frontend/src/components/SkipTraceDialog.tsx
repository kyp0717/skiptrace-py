import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import type { TownSkipTraceStats } from '@/services/api'

interface SkipTraceDialogProps {
  isOpen: boolean
  onClose: () => void
  stats: TownSkipTraceStats | null
  isLoading: boolean
  onProceed: () => void
}

export function SkipTraceDialog({
  isOpen,
  onClose,
  stats,
  isLoading,
  onProceed,
}: SkipTraceDialogProps) {
  const [isProcessing, setIsProcessing] = useState(false)

  const handleProceed = async () => {
    setIsProcessing(true)
    await onProceed()
    setIsProcessing(false)
  }

  if (isLoading) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Loading Skip Trace Information...</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  if (!stats) {
    return null
  }

  const needsSkipTrace = stats.untraced_cases > 0

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="text-xl">
            Skip Trace Status for {stats.town}
          </DialogTitle>
          <DialogDescription>
            {stats.scraped
              ? 'Review the skip trace status for this town'
              : 'This town has not been scraped yet'}
          </DialogDescription>
        </DialogHeader>

        {stats.scraped ? (
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <AlertCircle className="h-4 w-4 text-blue-600" />
                  <p className="text-sm font-medium text-blue-900">Total Cases</p>
                </div>
                <p className="text-2xl font-bold text-blue-700">{stats.total_cases}</p>
                <p className="text-xs text-blue-600 mt-1">Unique docket numbers</p>
              </div>

              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <p className="text-sm font-medium text-green-900">Already Traced</p>
                </div>
                <p className="text-2xl font-bold text-green-700">{stats.traced_cases}</p>
                <p className="text-xs text-green-600 mt-1">Completed lookups</p>
              </div>
            </div>

            {needsSkipTrace && (
              <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-amber-900">
                      {stats.untraced_cases} cases need skip tracing
                    </p>
                    <p className="text-xs text-amber-700 mt-1">
                      Estimated cost: ${(stats.untraced_cases * 0.07).toFixed(2)}
                      <span className="text-amber-600 ml-1">($0.07 per lookup)</span>
                    </p>
                  </div>
                </div>
              </div>
            )}

            {!needsSkipTrace && (
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-green-900">
                      All cases have been skip traced
                    </p>
                    <p className="text-xs text-green-700 mt-1">
                      No additional lookups needed for this town
                    </p>
                  </div>
                </div>
              </div>
            )}

            {stats.error && (
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-red-900">Error</p>
                    <p className="text-xs text-red-700 mt-1">{stats.error}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="py-6">
            <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-gray-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    No data available
                  </p>
                  <p className="text-xs text-gray-700 mt-1">
                    This town needs to be scraped first before skip tracing can be performed
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isProcessing}
          >
            Cancel
          </Button>
          {stats.scraped && needsSkipTrace && (
            <Button
              onClick={handleProceed}
              disabled={isProcessing}
              className="bg-pink-800 hover:bg-pink-900 text-white"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                `Skip Trace ${stats.untraced_cases} Cases`
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}