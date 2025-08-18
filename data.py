from pydantic import BaseModel


class VideoSearchResult(BaseModel):
    videoName: str
    title: str
    summary: str
    keywords: list
    durationSec: float
    s3URI: str
    keyframeURL: str
    score: float


class VideoSearchResults(BaseModel):
    results: list[VideoSearchResult]

    def to_dict(self):
        return {"results": [result.model_dump() for result in self.results]}


class VideoSegmentSearchResult(VideoSearchResult):
    segmentId: int
    startSec: float
    endSec: float
    embeddingOption: str
    segmentScore: float


class VideoSegmentSearchResults(BaseModel):
    results: list[VideoSegmentSearchResult]

    def to_dict(self):
        return {"results": [result.model_dump() for result in self.results]}

    def sorted_by_segment_score(self):
        return sorted(self.results, key=lambda x: x.segmentScore, reverse=True)
